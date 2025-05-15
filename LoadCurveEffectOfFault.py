import pandas as pd
import GraphSearch as gs
import MiscFunctions as mf
import GenerationFunctions as gf
import LoadCurve as lc

def loadCurveFaultEffects(fault, component, buses, sections, loads, generationData, backupFeeders, t, r, loadCurve=0, DERScurve = 0, DSEBF = True, RNG=False, DERS = False):
    """
    Calculates the effects of a fault on the system.

    Args:
        fault (int): The faulted section.
        component (str): The component affected by the fault (not in use anymore).
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.
        loads (DataFrame): Data about loads in the system.
        generationData (DataFrame): Data about generation in the system.
        backupFeeders (DataFrame): Data about backup feeders in the system.
        r (int): The fault duration.
        DSEBF (bool, optional): (Down Stream Effect of Backup Feeder) Flag indicating if backup feeders creates a outage on  the secondry side.
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

    r = max(s, r) #Sets a lower bound  of r at the switching time (mostly error prevention)

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
            'time': gs.switchingTime(i, switchingTimes),
            'ENS': lc.loadCurveSumEnergy(t, gs.switchingTime(i, switchingTimes), gs.findLoadPoints(i, loads), loads, loadCurve)
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
                'time': r,
                'ENS': lc.loadCurveSumEnergy(t, r, gs.findLoadPoints(i, loads), loads, loadCurve)
            })
        elif gs.mainPower(i[0], buses, sections, generationData):
            # Section connected to the main power source
            effectsOnSections.append({
                'state': 'connected',
                'loads': gs.findLoadPoints(i, loads),
                'time': 0,
                'ENS': 0
            })
        else:
            if DERS:
                if DERScurve:
                    ENS, uBackup = lc.LCandDERScurve(t, r, s, gs.findLoadPoints(i, loads), loads, loadCurve, generationData, i , DERScurve)
                else:
                    uBackup = gf.loadCurveDistributedGeneration(
                            lc.loadCurveSumEnergy(t+s, r-s, gs.findLoadPoints(i, loads), loads, loadCurve),
                            lc.loadPeak(t+s, r-s, gs.findLoadPoints(i, loads), loads, loadCurve),
                            generationData, 
                            i, 
                            r,
                            s) #Calculates the outage duration after local generation is utilized
            else:
                uBackup = r
            
            # Check for backup feeders
            connectedBackup = gs.findBackupFeeders(i, backupFeeders)
            if connectedBackup:
                for j in connectedBackup:
                    if gs.mainPower(j['otherEnd'], buses, sections, generationData):
                        if backupFeeders.at[j['backupFeeder'], 's'] < uBackup:
                            breaker = gs.findProtection(j['otherEnd'], buses, sections)
                            effectsOnSections.append({
                                'state': 'backupPower',
                                'loads': gs.findLoadPoints(i, loads),
                                'time': backupFeeders['s'][j['backupFeeder']],
                                'ENS': lc.loadCurveSumEnergy(t, backupFeeders['s'][j['backupFeeder']], gs.findLoadPoints(i, loads), loads, loadCurve)
                            })
                            if DSEBF:
                                if breaker['direction'] == 'D':
                                    endBus = sections['Upstream Bus'][breaker['section']]
                                else:
                                    endBus = breaker['bus']
                                connected = gs.connectedBetween(j['otherEnd'], endBus, buses, sections, connected=[])
                                effectsOnSections.append({
                                    'state': 'backup',
                                    'loads': gs.findLoadPoints(connected, loads),
                                    'time': s,
                                    'ENS': lc.loadCurveSumEnergy(t, s, gs.findLoadPoints(connected, loads), loads, loadCurve)
                                })
                        elif DERS:
                            # If DERS are enabled and are prefferential to BF, use local generation
                            if DERScurve:
                                effectsOnSections.append({
                                'state': 'localGenerationOverBF',
                                'loads': gs.findLoadPoints(i, loads),
                                'time': uBackup,
                                'ENS': ENS
                                })
                            else:
                                effectsOnSections.append({
                                    'state': 'localGenerationOverBF',
                                    'loads': gs.findLoadPoints(i, loads),
                                    'time': uBackup,
                                    'ENS': lc.loadCurveSumEnergy(t, uBackup, gs.findLoadPoints(i, loads), loads, loadCurve)
                                })
            elif DERS and uBackup < r:
                # If no backup feeder is available, use local generation
                if DERScurve:
                    effectsOnSections.append({
                                'state': 'localGenerationOverBF',
                                'loads': gs.findLoadPoints(i, loads),
                                'time': uBackup,
                                'ENS': ENS
                                })
                else:
                    effectsOnSections.append({
                                'state': 'localGenerationOverBF',
                                'loads': gs.findLoadPoints(i, loads),
                                'time': uBackup,
                                'ENS': lc.loadCurveSumEnergy(t, uBackup, gs.findLoadPoints(i, loads), loads, loadCurve)
                                })
            else:
                # No backup feeder available
                effectsOnSections.append({
                    'state': 'noBackup',
                    'loads': gs.findLoadPoints(i, loads),
                    'time': r,
                    'ENS': lc.loadCurveSumEnergy(t, r, gs.findLoadPoints(i, loads), loads, loadCurve)
                })



    #print('Effects on sections:', effectsOnSections)

    
    # Aggregate the effects on load points
    ''''
    ENS = 0
    effectsOnLPs = {}
    for LP in loads.index:
        LPeffects = {'U': 0, 'ENS': 0}
        effectsOnLPs[LP] = LPeffects
    for sec in effectsOnSections:
        ENS += sec['ENS']
        for LP in sec['loads']:
            if sec['time'] is None:
                sec['time'] = 0
            if sec['time'] > effectsOnLPs[LP]['U']:
                effectsOnLPs[LP]['U'] = sec['time']
    '''

    ENS = 0
    effectsOnLPs = {}
    for sec in effectsOnSections:
        ENS += sec['ENS']
        for LP in sec['loads']:
            if LP in effectsOnLPs:
                if sec['time'] is None:
                    sec['time'] = 0
                elif sec['time'] > effectsOnLPs[LP]:
                    effectsOnLPs[LP] = sec['time']
            else:
                if sec['time'] is None:
                    effectsOnLPs[LP] = 0
                else:
                    effectsOnLPs[LP] = sec['time']



    # Return the final effects on load points
    #print('Effects on load points:', effectsOnLPs)
    return effectsOnLPs, ENS


def tripProtection(fault, buses, sections):
    """
    Simulates the tripping of protection devices based on a fault.

    Args:
        fault (int): The faulted section.
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.

    Returns:
        tuple: Updated buses, sections, tripped protection details, and failure status.
    """
    section = fault
    # Check if the faulted section has upstream or bidirectional protection
    if sections['Fuse/breaker direction'][section] in ['U', 'B']:
        # Trip the upstream protection and update the buses and sections
        trippedProtection = {
            'section': section,
            'bus': sections['Upstream Bus'][section],
            'direction': 'U'
        }
        buses['Downstream Sections'][sections['Upstream Bus'][section]].remove(section)
        sections['Upstream Bus'][section] = 0
        return buses, sections, trippedProtection, False

    # Move to the upstream section to find protection
    section = buses['Upstream Section'][sections['Upstream Bus'][section]]
    while True:
        if section == 0:
            # If no protection is found, return failure
            return 0, 0, 0, True
        if sections['Fuse/breaker direction'][section] != 'N':
            # Check if the section has downstream or bidirectional protection
            if sections['Fuse/breaker direction'][section] in ['D', 'B']:
                trippedProtection = {
                    'section': section,
                    'bus': sections['Downstream Bus'][section],
                    'direction': 'D'
                }
                # Update buses and sections after tripping downstream protection
                buses['Upstream Section'][sections['Downstream Bus'][section]] = 0
                buses['Connected Sections'][sections['Downstream Bus'][section]].remove(section)
                sections['Downstream Bus'][section] = 0
                return buses, sections, trippedProtection, False
            else:
                # Trip upstream protection
                trippedProtection = {
                    'section': section,
                    'bus': sections['Upstream Bus'][section],
                    'direction': 'U'
                }
                buses['Downstream Sections'][sections['Upstream Bus'][section]].remove(section)
                buses['Connected Sections'][sections['Upstream Bus'][section]].remove(section)
                sections['Upstream Bus'][section] = 0
                return buses, sections, trippedProtection, False
        else:
            # Continue searching upstream for protection
            section = buses['Upstream Section'][sections['Upstream Bus'][section]]

def findProtection(bus, buses, sections):
    """
    Finds the protection device for a given bus.

    Args:
        bus (int): The bus to find protection for.
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.

    Returns:
        dict: Details of the protection device.
    """
    section = buses['Upstream Section'][bus]
    if sections['Fuse/breaker direction'][section] in ['U', 'B']:
        protection = {'section': section, 'bus': sections['Upstream Bus'][section], 'direction': 'U'}
        return protection
    else:
        section = buses['Upstream Section'][sections['Upstream Bus'][section]]
    while True:
        if sections['Fuse/breaker direction'][section] != 'N':
            if sections['Fuse/breaker direction'][section] in ['D', 'B']:
                protection = {'section': section, 'bus': sections['Downstream Bus'][section], 'direction': 'D'}
                return protection
            else:
                protection = {'section': section, 'bus': sections['Upstream Bus'][section], 'direction': 'U'}
                return protection
        else:
            section = buses['Upstream Section'][sections['Upstream Bus'][section]]


def disconnect(fault, buses, sections):
    """
    Disconnects sections based on a fault.

    Args:
        fault (int): The faulted section.
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.

    Returns:
        tuple: Updated buses, sections, and list of disconnectors.
    """
    if sections['Disconnector direction'][fault] == 'B':
        faultBus = 0
        disconnectors = []
        disconnectors.append({
                'line': fault,
                'fromBus': sections['Upstream Bus'][fault],
                's': sections['s'][fault],
                'toBus': sections['Downstream Bus'][fault]
            })
        disconnectors.append({
                'line': fault,
                'fromBus': sections['Downstream Bus'][fault],
                's': sections['s'][fault],
                'toBus': sections['Upstream Bus'][fault]
            })
    elif sections['Disconnector direction'][fault] == 'U':
        faultBus = sections['Downstream Bus'][fault]
    elif sections['Disconnector direction'][fault] == 'D':
        faultBus = sections['Upstream Bus'][fault]
    else:
        faultBus = sections['Downstream Bus'][fault]
        if faultBus == 0:
            faultBus = sections['Upstream Bus'][fault]
    if faultBus != 0:
        disconnectors = gs.disconnectorsDFS(faultBus, buses, sections, connected=[], disconnectors=[])

    openDisconnectors = []
    for i in disconnectors:
        if i['fromBus'] == sections['Upstream Bus'][i['line']]:
            if sections['Disconnector direction'][i['line']] in ['D', 'B']:
                openDisconnectors.append({'section': i['line'], 'direction': 'D'})
                buses['Upstream Section'][sections['Downstream Bus'][i['line']]] = 0
                if i['line'] in buses['Connected Sections'][sections['Downstream Bus'][i['line']]]:
                    buses['Connected Sections'][sections['Downstream Bus'][i['line']]].remove(i['line'])
                sections['Downstream Bus'][i['line']] = 0
            else:
                openDisconnectors.append({'section': i['line'], 'direction': 'U'})
                if i['line'] in buses['Downstream Sections'][sections['Upstream Bus'][i['line']]]:
                    buses['Downstream Sections'][sections['Upstream Bus'][i['line']]].remove(i['line'])
                if i['line'] in buses['Connected Sections'][sections['Upstream Bus'][i['line']]]:
                    buses['Connected Sections'][sections['Upstream Bus'][i['line']]].remove(i['line'])
                sections['Upstream Bus'][i['line']] = 0
        else:
            if sections['Disconnector direction'][i['line']] in ['U', 'B']:
                openDisconnectors.append({'section': i['line'], 'direction': 'U'})
                if i['line'] in buses['Downstream Sections'][sections['Upstream Bus'][i['line']]]:
                    buses['Downstream Sections'][sections['Upstream Bus'][i['line']]].remove(i['line'])
                if i['line'] in buses['Connected Sections'][sections['Upstream Bus'][i['line']]]:
                    buses['Connected Sections'][sections['Upstream Bus'][i['line']]].remove(i['line'])
                sections['Upstream Bus'][i['line']] = 0
            else:
                openDisconnectors.append({'section': i['line'], 'direction': 'D'})
                buses['Upstream Section'][sections['Downstream Bus'][i['line']]] = 0
                if i['line'] in buses['Connected Sections'][sections['Downstream Bus'][i['line']]]:
                    buses['Connected Sections'][sections['Downstream Bus'][i['line']]].remove(i['line'])
                sections['Downstream Bus'][i['line']] = 0

    return buses, sections, disconnectors


def reconnectProtection(buses, sections, trippedProtection, fault):
    """
    Reconnects protection devices after a fault.

    Args:
        buses (DataFrame): Data about buses in the system.
        sections (DataFrame): Data about sections in the system.
        trippedProtection (dict): Details of the tripped protection device.
        fault (int): The faulted section.

    Returns:
        tuple: Updated buses and sections.
    """
    if sections['Upstream Bus'][fault] != 0:
        if gs.protectionNeededTestDFS(sections['Upstream Bus'][fault], buses, sections, trippedProtection, connected=[], needed=False):
            return buses, sections
    elif sections['Downstream Bus'][fault] != 0:
        if gs.protectionNeededTestDFS(sections['Downstream Bus'][fault], buses, sections, trippedProtection, connected=[], needed=False):
            return buses, sections
    if trippedProtection['direction'] == 'U':
        sections.loc[trippedProtection['section'], 'Upstream Bus'] = trippedProtection['bus']
        buses['Downstream Sections'][trippedProtection['bus']].append(trippedProtection['section'])
        buses['Connected Sections'][trippedProtection['bus']].append(trippedProtection['section'])
    else:
        sections.loc[trippedProtection['section'], 'Downstream Bus'] = trippedProtection['bus']
        buses['Upstream Section'][trippedProtection['bus']] = trippedProtection['section']
        buses['Connected Sections'][trippedProtection['bus']].append(trippedProtection['section'])
    return buses, sections