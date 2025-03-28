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
    # Initialize a list to store the effects on sections
    effectsOnSections = []

    # Trip protection devices and check if the entire system is down
    buses, sections, trippedProtection, fullSystemDown = gs.tripProtection(fault, buses, sections)

    # If the entire system is down, return fault duration for all load points
    if fullSystemDown:
        effectsOnLPs = {}
        for i, row in loads.iterrows():
            effectsOnLPs[i] = r
        return effectsOnLPs

    # Isolate the faulted section and identify disconnectors
    buses, sections, disconnectors = gs.disconnect(fault, buses, sections)

    # Determine the maximum switching time among disconnectors
    s = 0
    for i in disconnectors:
        if i['s'] > s:
            s = i['s']

    # Calculate switching times for each bus
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

    # Identify all isolated interconnections in the system
    disconnectedSections = gs.findConnectedSegments(buses, sections)

    # Record the effects on disconnected sections
    for i in disconnectedSections:
        effectsOnSections.append({
            'state': 'tripped',
            'loads': gs.findLoadPoints(i, loads),
            'time': gs.switchingTime(i, switchingTimes)
        })

    # Reconnect protection devices and update the system state
    buses, sections = gs.reconnectProtection(buses, sections, trippedProtection, fault)

    # Identify disconnected sections again after reconnection
    disconnectedSections = gs.findConnectedSegments(buses, sections)

    for i in disconnectedSections:
        if sections['Upstream Bus'][fault] in i or sections['Downstream Bus'][fault] in i:
            # Faulted section
            effectsOnSections.append({
                'state': 'fault',
                'loads': gs.findLoadPoints(i, loads),
                'time': r
            })
        elif gs.mainPower(i[0], buses, sections, generationData):
            # Section connected to the main power source
            effectsOnSections.append({
                'state': 'connected',
                'loads': gs.findLoadPoints(i, loads),
                'time': 0
            })
        else:
            # Check for backup feeders
            connectedBackup = gs.findBackupFeeders(i, backupFeeders)
            if connectedBackup:
                for j in connectedBackup:
                    if gs.mainPower(j['otherEnd'], buses, sections, generationData):
                        breaker = gs.findProtection(j['otherEnd'], buses, sections)
                        effectsOnSections.append({
                            'state': 'backupPower',
                            'loads': gs.findLoadPoints(i, loads),
                            'time': backupFeeders['s'][j['backupFeeder']]
                        })
                        if breaker['direction'] == 'D':
                            endBus = sections['Upstream Bus'][breaker['section']]
                        else:
                            endBus = breaker['bus']
                        connected = gs.connectedBetween(j['otherEnd'], endBus, buses, sections, connected=[])
                        effectsOnSections.append({
                            'state': 'backup',
                            'loads': gs.findLoadPoints(connected, loads),
                            'time': s
                        })
                        break
            else:
                # No backup feeder available
                effectsOnSections.append({
                    'state': 'noBackup',
                    'loads': gs.findLoadPoints(i, loads),
                    'time': r
                })

    # Aggregate the effects on load points
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

    # Return the final effects on load points
    return effectsOnLPs