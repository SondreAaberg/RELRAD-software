import numpy as np
import random as rng


def distributedGeneration(loads, generation, connection, u):
    powerNeded = 0
    energyNeeded = 0
    energyAvailable = 0
    powerAvailable = 0

    for i in connection:
        if i in loads.index:
            powerNeded += loads['Load point peak [MW]'][i]
            energyNeeded += loads['Load level average [MW]'][i] * u
        if i in generation.index:
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
            

#def distributedGenerationRNG(loads, generation, connection, u):

def PV(t, Pr, R_c, G_std, G_max, LDI):
    month = t/(8736*30)
    day = (month - np.floor(month)) * 30
    hour = (day - np.floor(day)) * 24

    if hour == 0 or np.round(hour) == 0:
        hour = 24
    
    month = np.ceil(month)
    day = np.ceil(day)
    if (hour-np.floor(hour)) < 0.0001:
        hour = np.round(hour)
    else:
        hour = np.ceil(hour)

    f = rng.uniform(0, 1)
    if hour >= 6 and hour < 18:
        G_d = G_max*((-1/36*hour)**2 + 2/(3*hour) - 3)
        G = (G_d + f)*LDI[month]
    else:
        G = 0

    if G >= 0 and G < R_c:
        production_PV = Pr * G^2/(G_std * R_c)
    elif G >= R_c and G <= G_std:
        production_PV = Pr * G/G_std
    else:
        production_PV = Pr

    return production_PV

#def WP():

#def BESS():
        