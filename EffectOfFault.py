import pandas as pd
import GraphSearch as gs
import MiscFunctions as mf



def faultEffects(fault, component, buses, sections, loads, generationData, backupFeeders, r, RNG=False):
    """
    Calculates the effects of a fault on the system.

    Args:
        fault (int): The faulted section.
        component (str): The component affected by the fault.
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.
        loads (DataFrame): Data about loads in the system.
        generationData (DataFrame): Data about generation in the system.
        backupFeeders (DataFrame): Data about backup feeders in the system.
        r (int): The fault duration.
        RNG (bool, optional): Flag indicating if random number generation is used. Defaults to False.

    Returns:
        dict: Effects of the fault on load points.
    """
    effectsOnSections = []

    buses, sections, trippedProtection, fullSystemDown = tripProtection(fault, buses, sections)

    if fullSystemDown:
        effectsOnLPs = {}
        for i, row in loads.iterrows():
            effectsOnLPs[i] = r
        return effectsOnLPs

    buses, sections, disconnectors = disconnect(fault, buses, sections)

    s = 0
    for i in disconnectors:
        if i['s'] > s:
            s = i['s']

    switchingTimes = {}
    for i in disconnectors:
        if i['fromBus'] not in switchingTimes:
            switchingTimes[i['fromBus']] = i['s']
        else:
            if i['s'] > switchingTimes[i['fromBus']]:
                switchingTimes[i['fromBus']] = i['s']
        if i['toBus'] not in switchingTimes:
            switchingTimes[i['toBus']] = i['s']
        else:
            if i['s'] > switchingTimes[i['toBus']]:
                switchingTimes[i['toBus']] = i['s']

    disconnectedSections = findConnectedSegments(buses, sections)

    for i in disconnectedSections:
        effectsOnSections.append({
            'state': 'tripped',
            'loads': findLoadPoints(i, loads),
            'time': switchingTime(i, switchingTimes)
        })

    buses, sections = reconnectProtection(buses, sections, trippedProtection, fault)

    disconnectedSections = findConnectedSegments(buses, sections)

    for i in disconnectedSections:
        if sections['Upstream Bus'][fault] in i or sections['Downstream Bus'][fault] in i:
            effectsOnSections.append({
                'state': 'fault',
                'loads': findLoadPoints(i, loads),
                'time': r
            })
        elif mainPower(i[0], buses, sections, generationData):
            effectsOnSections.append({
                'state': 'connected',
                'loads': findLoadPoints(i, loads),
                'time': 0
            })
        else:
            connectedBackup = findBackupFeeders(i, backupFeeders)
            if connectedBackup:
                for j in connectedBackup:
                    if mainPower(j['otherEnd'], buses, sections, generationData):
                        breaker = findProtection(j['otherEnd'], buses, sections)
                        effectsOnSections.append({
                            'state': 'backupPower',
                            'loads': findLoadPoints(i, loads),
                            'time': backupFeeders['s'][j['backupFeeder']]
                        })
                        if breaker['direction'] == 'D':
                            endBus = sections['Upstream Bus'][breaker['section']]
                        else:
                            endBus = breaker['bus']
                        connected = connectedBetween(j['otherEnd'], endBus, buses, sections, connected=[])
                        effectsOnSections.append({
                            'state': 'backup',
                            'loads': findLoadPoints(connected, loads),
                            'time': s
                        })
                        break
            else:
                effectsOnSections.append({
                    'state': 'noBackup',
                    'loads': findLoadPoints(i, loads),
                    'time': r
                })

    effectsOnLPs = {}
    for i in effectsOnSections:
        for LP in i['loads']:
            if LP in effectsOnLPs:
                if i['time'] is None:
                    i['time'] = 0
                elif i['time'] > effectsOnLPs[LP]:
                    effectsOnLPs[LP] = i['time']
            else:
                if i['time'] is None:
                    effectsOnLPs[LP] = 0
                else:
                    effectsOnLPs[LP] = i['time']

    return effectsOnLPs