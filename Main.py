import pandas as pd
import MonteCarloSimulation as mc
import RELRAD as rr
import copy
from concurrent.futures import ThreadPoolExecutor

def createSystem(file_path):
    """
    Creates the system by reading data from Excel files.

    Args:
        file_path (str): Path to the Excel file containing system data.

    Returns:
        dict: A dictionary containing data about buses, sections, loads, components, backup feeders, and generation.
    """
    system = {}
    # Load data for buses, sections, loads, components, backup feeders, and generation
    system['buses'] = pd.read_excel(file_path, 'Bus Data', index_col=0)
    system['sections'] = pd.read_excel(file_path, 'Line Data', index_col=0)
    system['loads'] = pd.read_excel(file_path, 'Load Point Data', index_col=0)
    system['components'] = pd.read_excel(file_path, 'Component Data', index_col=0)
    system['backupFeeders'] = pd.read_excel(file_path, 'Backup Feeders', index_col=0)
    system['generationData'] = pd.read_excel(file_path, 'Generation Data', index_col=0)

    # Initialize columns for buses and sections
    system['buses']['Upstream Section'] = str(0)
    system['buses']['Downstream Sections'] = [list() for _ in range(len(system['buses'].index))]
    system['buses']['Connected Sections'] = [list() for _ in range(len(system['buses'].index))]
    system['sections']['s'] = float(0)
    system['sections']['Components'] = {}

    # Initialize columns for loads
    system['loads']['U'] = float(0)
    system['loads']['nrOfFaults'] = int(0)
    system['loads']['R'] = float(0)
    system['loads']['Lambda'] = float(0)

    # Fix buses and calculate failure rates
    system['buses'] = mf.fixbuses(system['buses'], system['sections'])
    system['sections'] = mf.calcFailRates(system['sections'], system['components'])

    return system

# Function to perform reliability analysis (RELRAD)
def RELRAD(loc, outFile):


    system = createSystem(loc)
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
    for sec, row in system['sections'].iterrows():
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
    for sec in system['sections'].index:
        for comp in system['sections']['Components'][sec]:
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

# Function to perform Monte Carlo simulation for reliability analysis
def MonteCarlo(loc, n, outFile):
    # Load data from Excel files and create the system
    system = createSystem(loc)
    
    h = 8736  # Total hours in a year


    # Perform Monte Carlo simulation for n years (multithreaded)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(mf.MonteCarloYear, system['sections'], system['buses'], system['loads'], system['generationData'], system['backupFeeders']) for year in range(n)]

        for future in futures:
            results = future.result()
            for i in system['loads'].index:
                system['loads'].at[i, 'nrOfFaults'] += results[i]['nrOfFaults']
                system['loads'].at[i,'U'] += results[i]['U']
    

    # Calculate average failure rate and unavailability for each load point
    for LP in system['loads'].index:
        system['loads'].at[LP, 'Lambda'] = system['loads'].at[LP, 'nrOfFaults'] / n
        system['loads'].at[LP, 'U']/= n

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


#RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214.xlsx')
#MonteCarlo('RBMC p214.xlsx', 5000, 'MonteCarloResultsRBMCp214.xlsx')
'''
mc.MonteCarlo('BUS 4.xlsx', 'MonteCarloResultsBUS4.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('BUS 4.xlsx', 'RELRADResultsBUS4.xlsx', DSEBF = False)
mc.MonteCarlo('RBMC p214.xlsx', 'MonteCarloResultsRBMCp214.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('RBMC p214.xlsx', 'RELRADResultsRBMCp214.xlsx', DSEBF = False)
mc.MonteCarlo('BUS 2.xlsx', 'MonteCarloResultsBUS2.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('BUS 2.xlsx', 'RELRADResultsBUS2.xlsx', DSEBF = False)
mc.MonteCarlo('BUS 6.xlsx', 'MonteCarloResultsBUS6.xlsx', beta=0.02, DSEBF = False)
rr.RELRAD('BUS 6.xlsx', 'RELRADResultsBUS6.xlsx', DSEBF = False)
mc.MonteCarlo('SimpleTest.xlsx', 'MonteCarloResultsSimpleTest.xlsx', beta=0.02, DSEBF = False, DERS=False)
rr.RELRAD('SimpleTest.xlsx', 'RELRADResultsSimpleTest.xlsx', DSEBF = False, DERS=False)
'''

mc.MonteCarlo('BUS 2.xlsx', 'MonteCarloResultsBUS2TEST.xlsx', beta=0.02, DSEBF = False, LoadCurve=True)