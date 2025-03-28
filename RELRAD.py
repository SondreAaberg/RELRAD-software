import pandas as pd
import GraphSearch as gs
import MiscFunctions as mf
import CreateSystem as cs
import copy
from concurrent.futures import ThreadPoolExecutor

def RELRAD(loc, outFile):


    system = cs.createSystem(loc)
    '''
    # Load data from Excel files
    buses = pd.read_excel(loc, 'Bus Data', index_col=0)
    sections = pd.read_excel(loc, 'Line Data', index_col=0)
    loads = pd.read_excel(loc, 'Load Point Data', index_col=0)
    components = pd.read_excel(loc, 'Component Data', index_col=0)
    backupFeeders = pd.read_excel(loc, 'Backup Feeders', index_col=0)
    generationData = pd.read_excel(loc, 'Generation Data', index_col=0)

    # Fix buses and calculate failure rates for the original data
    busesOriginal = mf.fixbuses(buses, sections)
    sectionsOriginal = mf.calcFailRates(sections, components)
    '''
    # Create a list of all components in the system
    componentList = []
    for sec in system['sections'].index:
        for comp in system['sections']['Components'][sec]:
            componentTag = sec + comp
            componentList.append(componentTag)

    # Create a list of load points (LPs) with different states
    LPs = []
    for i in system['loads'].index:
        LPs.append(i + 'l')  # Load point lambda
        LPs.append(i + 'r')  # Load point repair time
        LPs.append(i + 'U')  # Load point unavailability

    # Initialize a DataFrame to store results
    results = pd.DataFrame(index=componentList, columns=LPs)

    # Iterate through each section and component to calculate effects on load points
    for sec, row in system['sections'].iterrows():
        for comp in system['sections']['Components'][sec]:
            print(sec, comp)
            # Create deep copies of the original data for analysis
            sectionsCopy = pd.DataFrame(columns=system['sections'].columns,
                                        data=copy.deepcopy(system['sections'].values),
                                        index=system['sections'].index)
            busesCopy = pd.DataFrame(columns=system['buses'].columns,
                                     data=copy.deepcopy(system['buses'].values),
                                     index=system['buses'].index)
            
            # Calculate the effects of faults on load points
            effectOnLPs = gs.faultEffects(sec, comp, busesCopy, sectionsCopy, system['loads'], system['generationData'], system['backupFeeders'], system['sections']['Components'][sec][comp]['r'])
            componentTag = sec + comp
            for LP in effectOnLPs:
                if effectOnLPs[LP] > 0:
                    # Update results for the load point
                    results.loc[componentTag, LP + 'l'] = system['sections']['Components'][sec][comp]['lambda']
                    results.loc[componentTag, LP + 'r'] = effectOnLPs[LP]
                    results.loc[componentTag, LP + 'U'] = system['sections']['Components'][sec][comp]['lambda'] * effectOnLPs[LP]
                    # Update load point data
                    system['loads'].loc[LP, 'Lambda'] += system['sections']['Components'][sec][comp]['lambda']
                    system['loads'].loc[LP, 'U'] += system['sections']['Components'][sec][comp]['lambda'] * effectOnLPs[LP]

    # Print and save results
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
    # Print and save results        
    system['loads'].to_excel(outFile, sheet_name='Load Points')
    print(system['loads'])