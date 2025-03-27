
def distributedGeneration(loads, generation, connection, u):
    powerNeded = 0
    energyNeeded = 0 
    energyAvailable = 0 
    powerAvailable = 0

    for i in connection:
        if i in loads:
            powerNeded += loads['Load point peak [MW]'][i]
            energyNeeded += loads['Load level average [MW]'][i] * u
        if i in generation:
            if generation['Lim MW'][i] == 'Inf' and generation['E cap'][i] != 'Inf':
                return 0
            powerAvailable += generation['Lim MW'][i]
            if generation['E cap'][i] != 'Inf':
                energyAvailable += generation['E cap'][i]
            else:
                energyAvailable += generation['Lim MW'][i] * u

    if energyAvailable > energyNeeded and powerAvailable > powerNeded:
        return 0
    else:
        if powerAvailable > powerNeded:
            return u*(energyAvailable/energyNeeded)
        else:
            return u
            
        