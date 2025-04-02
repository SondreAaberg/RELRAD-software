import pandas as pd
import numpy as np
import random as rng
import GraphSearch as gs
import MiscFunctions as mf
import CreateSystem as cs
import EffectOfFault as ef
import VarianceCalculations as vc
import copy
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


def MonteCarlo(loc, outFile, CL = 0.95, beta = 0.05, nCap = 0, DSEBF = True):
    lock = Lock()
    # Load data from Excel files and create the system
    system = cs.createSystem(loc)
    h = 8736  # Total hours in a year
    # Perform Monte Carlo simulation for 600 years to find variance of EENS (multithreaded)
    n1 = 600
    EENS = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(MonteCarloYear, system['sections'], system['buses'], system['loads'], system['generationData'], system['backupFeeders'], DSEBF=DSEBF) for year in range(n1)]

        for future in futures:
            yealyEENS = 0
            results = future.result()
            for LP in results:
                yealyEENS += results[LP]['U'] * system['loads'].at[LP, 'Load level average [MW]']
            EENS.append(yealyEENS)
            with lock:
                for i in system['loads'].index:
                    system['loads'].at[i, 'nrOfFaults'] += results[i]['nrOfFaults']
                    system['loads'].at[i,'U'] += results[i]['U']

    EENS = np.array(EENS)

    #n2 = vc.calculate_iterations(CL, np.std(EENS), beta)  # Calculate number of simulations needed for desired confidence level and margin of error
    n2 = vc.calcNumberOfSimulations(EENS, beta)  # Calculate number of simulations needed for desired variance

    n2 = int(np.ceil(float(n2)*1.25))  # Increase number of simulations to 1.25 times the calculated value to compensate for inaccuracy in variance calculation 
    
    if nCap > 0 and n2 > nCap: #Caps the number of simulations to nCap
        n2 = nCap
    
    n2 = max(0, n2 - n1) # Subtracts the already performed simulations from the total number of simulations needed

    
    if n2 > 0:
        # Perform Monte Carlo simulation for n years (multithreaded)
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(MonteCarloYear, system['sections'], system['buses'], system['loads'], system['generationData'], system['backupFeeders'], DSEBF=DSEBF) for year in range(n2)]
            for future in futures:
                for LP in results:
                    yealyEENS += results[LP]['U'] * system['loads'].at[LP, 'Load level average [MW]']
                EENS = np.append(EENS, yealyEENS)
                results = future.result()
                with lock:
                    for i in system['loads'].index:
                        system['loads'].at[i, 'nrOfFaults'] += results[i]['nrOfFaults']
                        system['loads'].at[i,'U'] += results[i]['U']
    
    trueBeta = vc.calcBeta(EENS)  # Calculate the beta value for the EENS values

    # Calculate average failure rate and unavailability for each load point
    for LP in system['loads'].index:
        system['loads'].at[LP, 'Lambda'] = system['loads'].at[LP, 'nrOfFaults'] / (n2+n1)
        system['loads'].at[LP, 'U']/= (n2+n1)

    system['loads']['R'] = system['loads']['U'] / system['loads']['Lambda']
    system['loads']['SAIFI'] = system['loads']['Lambda'] * system['loads']['Number of customers']
    system['loads']['SAIDI'] = system['loads']['U'] * system['loads']['Number of customers']
    system['loads']['CAIDI'] = system['loads']['R'] * system['loads']['Number of customers']
    system['loads']['EENS'] = system['loads']['U'] * system['loads']['Load level average [MW]']

    system['loads'].at['TOTAL', 'Number of customers'] = system['loads']['Number of customers'].sum()
    system['loads'].at['TOTAL', 'Load level average [MW]'] = system['loads']['Load level average [MW]'].sum()
    system['loads'].at['TOTAL', 'Load point peak [MW]'] = system['loads']['Load point peak [MW]'].sum()
    system['loads'].at['TOTAL', 'SAIFI'] = system['loads']['SAIFI'].sum() / (system['loads'].at['TOTAL', 'Number of customers'])
    system['loads'].at['TOTAL', 'SAIDI'] = system['loads']['SAIDI'].sum() / (system['loads'].at['TOTAL', 'Number of customers'])
    system['loads'].at['TOTAL', 'CAIDI'] = system['loads'].at['TOTAL', 'SAIDI'] / system['loads'].at['TOTAL', 'SAIFI']
    system['loads'].at['TOTAL', 'EENS'] = system['loads']['EENS'].sum()
    system['loads'].at['TOTAL', 'nr of simulations'] = n1 + n2
    system['loads'].at['TOTAL', 'provided beta'] = beta
    system['loads'].at['TOTAL', 'calculated beta'] = trueBeta
    # Print and save results        
    system['loads'].to_excel(outFile, sheet_name='Load Points')




def GenerateHistory (l, r):
    TTF = (-1/l) * np.log(rng.uniform(0,0.999)) * 8736
    TTR = -r * np.log(rng.uniform(0,0.999))
    return TTF, TTR


def minTTF(history):
    TTFcomponent = next(iter(history))
    TTF = history[TTFcomponent]['TTF']
    for secComp in history:
        if history[secComp]['TTF'] < TTF:
            TTFcomponent = secComp
            TTF = history[secComp]['TTF']
    return TTFcomponent


def MonteCarloYear(sectionsOriginal, busesOriginal, loads, generationData, backupFeeders, DSEBF=True):
    h = 8736  # Total hours in a year
    results = {}
    for i in loads.index:
        results[i] = {'nrOfFaults': 0, 'U': 0}
    history = {}
        # Generate failure history for each component
    for sec in sectionsOriginal.index:
        for comp in sectionsOriginal['Components'][sec]:
            TTF, TTR = GenerateHistory(sectionsOriginal['Components'][sec][comp]['lambda'], sectionsOriginal['Components'][sec][comp]['r'])
            history[sec + comp] = {
                'sec': sec,
                'comp': comp,
                'TTF': TTF,
                'TTR': TTR,
                'l': sectionsOriginal['Components'][sec][comp]['lambda'],
                'r': sectionsOriginal['Components'][sec][comp]['r']}

        # Find the first fault to occur
    fault = minTTF(history)
    while history[fault]['TTF'] < h:
            # Create deep copies of the original data for analysis
        sectionsCopy = pd.DataFrame(columns=sectionsOriginal.columns,
                                    data=copy.deepcopy(sectionsOriginal.values),
                                    index=sectionsOriginal.index)
        busesCopy = pd.DataFrame(columns=busesOriginal.columns,
                                    data=copy.deepcopy(busesOriginal.values),
                                    index=busesOriginal.index)
            
            # Calculate the effects of faults on load points
        effectOnLPs = ef.faultEffects(history[fault]['sec'], history[fault]['comp'], busesCopy, sectionsCopy, loads, generationData, backupFeeders, history[fault]['TTR'], DSEBF=DSEBF)
            
        for LP in effectOnLPs:
            if effectOnLPs[LP] > 0:
                # Update load point data
                results[LP]['nrOfFaults'] += 1
                results[LP]['U'] += effectOnLPs[LP]

        # Generate new failure history for the faulted component
        newTTF, newTTR = GenerateHistory(history[fault]['l'], history[fault]['r'])

        history[fault]['TTF'] += newTTF + history[fault]['TTR']
        history[fault]['TTR'] = newTTR
        fault = minTTF(history)
    return results