import pandas as pd


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
    system['buses'] = fixbuses(system['buses'], system['sections'])
    system['sections'] = calcFailRates(system['sections'], system['components'])

    return system



def fixbuses(buses, sections):
    """
    Updates the buses DataFrame with upstream, downstream, and connected sections.

    Args:
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.

    Returns:
        DataFrame: Updated buses DataFrame.
    """
    for bus in buses.index:
        upstream_section = 0
        downstream_sections = []
        for section in sections.index:
            if sections['Upstream Bus'][section] == bus:
                downstream_sections.append(section)
            if sections['Downstream Bus'][section] == bus:
                upstream_section = section
        buses['Upstream Section'][bus] = upstream_section
        buses['Downstream Sections'][bus] = downstream_sections
        buses['Connected Sections'][bus] = downstream_sections.copy()
        buses['Connected Sections'][bus].append(upstream_section)
    return buses



def calcFailRates(sections, components):
    for i, row in sections.iterrows():
        secComponents = {}
        secComponents['line'] = {'type': sections['Cable Type'][i], 'length': sections['Length'][i], 'lambda': components['lambda'][sections['Cable Type'][i]] * sections['Length'][i], 'r': components['r'][sections['Cable Type'][i]], 's': components['s'][sections['Cable Type'][i]]}
        if sections['Nr Transformers'][i]:
            secComponents['transformer'] = {'type': sections['Transformer Type'][i], 'lambda': components['lambda'][sections['Transformer Type'][i]] * sections['Nr Transformers'][i], 'r': components['r'][sections['Transformer Type'][i]], 's': components['s'][sections['Transformer Type'][i]]}
        #if sections['Nr Breaker'][i]:
            #sections.iloc[i,'lambda'] += components['lambda'][sections['Breaker Type'][i]] * sections['Nr Breaker'][i]
        sections['s'][i] = components['s'][sections['Cable Type'][i]]
        sections['Components'][i] = secComponents
    return sections


