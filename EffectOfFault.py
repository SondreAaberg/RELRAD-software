import GraphSearch as GS



def faultEffects(fault, component, buses, sections, loads, generationData, backupFeeders):
    
    r = sections['Components'][fault][component]['r']
    effectsOnSections = []

    buses, sections, trippedProtection, fullSystemDown = GS.tripProtection(fault, buses, sections)

    if fullSystemDown:
        effectsOnLPs = {}
        for i, row in loads.iterrows():
            effectsOnLPs[i] = r
        return effectsOnLPs


    buses, sections, disconnectors = GS.disconnect(fault, buses, sections)


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
    

    
    disconnectedSections = GS.findConnectedSegments(buses, sections)

    for i in disconnectedSections:
        effectsOnSections.append({'state': 'tripped', 'loads': GS.findLoadPoints(i, loads), 'time': GS.switchingTime(i, switchingTimes)})


    buses, sections = GS.reconnectProtection(buses, sections, trippedProtection, fault)

    disconnectedSections = GS.findConnectedSegments(buses, sections)

    

    for i in disconnectedSections:
        if sections['Upstream Bus'][fault] in i or sections['Downstream Bus'][fault] in i:
            effectsOnSections.append({'state': 'fault', 'loads': GS.findLoadPoints(i, loads), 'time': r})
        elif GS.mainPower(i[0], buses, sections, generationData):
            effectsOnSections.append({'state': 'connected', 'loads': GS.findLoadPoints(i, loads), 'time': 0})
        else:
            connectedBackup = GS.findBackupFeeders(i, backupFeeders)
            if connectedBackup:
                for j in connectedBackup:
                    if GS.mainPower(j['otherEnd'], buses, sections, generationData):
                        breaker = GS.findProtection(j['otherEnd'], buses, sections)
                        effectsOnSections.append({'state': 'backupPower', 'loads': GS.findLoadPoints(i, loads), 'time': backupFeeders['s'][j['backupFeeder']]})
                        if breaker['direction'] == 'D':
                            endBus = sections['Upstream Bus'][breaker['section']]
                        else:
                            endBus = breaker['bus']
                        connected = GS.connectedBetween(j['otherEnd'], endBus, buses, sections, connected = [])
                        effectsOnSections.append({'state': 'backup', 'loads': GS.findLoadPoints(connected, loads), 'time': s})
                        break
            else:
                effectsOnSections.append({'state': 'noBackup', 'loads': GS.findLoadPoints(i, loads), 'time': r})
    
    effectsOnLPs = {}
    for i in effectsOnSections:
        for LP in i['loads']:
            if LP in effectsOnLPs:
                if i['time'] == None:
                    i['time'] = 0
                elif i['time'] > effectsOnLPs[LP]:
                    effectsOnLPs[LP] = i['time']
            else:
                if i['time'] == None:
                    effectsOnLPs[LP] = 0
                else:
                    effectsOnLPs[LP] = i['time']



    return effectsOnLPs


    
    #connections = findConnectedSegments(buses, sections)

    #connectionsWithBackup = findBackupFeeders(connections, backupFeeders)

    #mainPower()