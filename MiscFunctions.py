import pandas as pd
import random as rng
import numpy as np
import copy
import GraphSearch as gs

def fixbuses(buses, sections):
    """
    Updates the buses DataFrame with upstream, downstream, and connected sections.

    Args:
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.

    Returns:
        DataFrame: Updated buses DataFrame.
    """
    for bus_id, _ in buses.iterrows():
        upstream_section = 0
        downstream_sections = []
        for section_id, _ in sections.iterrows():
            if sections['Upstream Bus'][section_id] == bus_id:
                downstream_sections.append(section_id)
            if sections['Downstream Bus'][section_id] == bus_id:
                upstream_section = section_id
        buses['Upstream Section'][bus_id] = upstream_section
        buses['Downstream Sections'][bus_id] = downstream_sections
        buses['Connected Sections'][bus_id] = downstream_sections.copy()
        buses['Connected Sections'][bus_id].append(upstream_section)
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


def MonteCarloYear(sectionsOriginal, busesOriginal, loads, generationData, backupFeeders):
    h = 8736  # Total hours in a year
    results = {}
    for i in loads.index:
        results[i] = {'nrOfFaults': 0, 'U': 0}
    history = {}
        # Generate failure history for each component
    for sec, row in sectionsOriginal.iterrows():
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
        effectOnLPs = gs.faultEffects(history[fault]['sec'], history[fault]['comp'], busesCopy, sectionsCopy, loads, generationData, backupFeeders, history[fault]['TTR'])
            
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