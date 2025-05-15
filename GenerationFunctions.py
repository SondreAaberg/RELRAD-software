import numpy as np
import random as rng


def distributedGeneration(loads, generationData, connection, r, s):


    powerAvailable = 0
    energyStorage = 0
    powerNeeded = 0
    energyNeeded = 0
    for i in connection:
        if i in generationData.index:
            if generationData['Lim MW'][i] > 0 and generationData['E cap'][i] == 0:
                powerAvailable += generationData['Lim MW'][i]
                energyNeeded -= generationData['Lim MW'][i] * (r-s)
            elif generationData['Lim MW'][i] > 0 and generationData['E cap'][i] > 0:
                energyStorage += generationData['E cap'][i]
                powerAvailable += generationData['Lim MW'][i]
        if i in loads.index:
            #print('i in loads.index', i)
            powerNeeded += loads['Load point peak [MW]'][i]
            energyNeeded += loads['Load level average [MW]'][i] * (r-s)

    #print('powerNeded', powerNeded)
    #print('energyNeeded', energyNeeded)
    #print('powerAvailable', powerAvailable)
    #print('energyAvailable', energyAvailable)


    if energyStorage > energyNeeded and powerAvailable > powerNeeded:
        return 0
    else:
        if powerAvailable > powerNeeded and energyNeeded > 0:
            u = (r-s) - (r-s)*(energyStorage/energyNeeded)
            return min(r, u+s)
        else:
            return r
        

def loadCurveDistributedGeneration(energyNeeded, powerNeeded, generationData, connection, r, s):
    #energyAvailable = 0
    #powerAvailable = 0

    powerAvailable = 0
    energyStorage = 0
    energyNeeded = 0
    for i in connection:
        if i in generationData.index:
            if generationData['Lim MW'][i] > 0 and generationData['E cap'][i] == 0:
                powerAvailable += generationData['Lim MW'][i]
                powerNeeded -= generationData['Lim MW'][i] * (r-s)
            elif generationData['Lim MW'][i] > 0 and generationData['E cap'][i] > 0:
                energyStorage += generationData['E cap'][i]
                powerAvailable += generationData['Lim MW'][i]


    #print('powerNeded', powerNeded)
    #print('energyNeeded', energyNeeded)
    #print('powerAvailable', powerAvailable)
    #print('energyAvailable', energyAvailable)


    if energyStorage > energyNeeded and powerAvailable > powerNeeded:
        return 0
    else:
        if powerAvailable > powerNeeded and energyNeeded > 0:
            u = (r-s) - (r-s)*(energyStorage/energyNeeded)
            return min(r, u+s)
        else:
            return r




    '''
    for i in connection:
        if i in generation.index:
            if generation['E cap'][i] > 0:
                powerAvailable += generation['Lim MW'][i]
                energyAvailable += generation['E cap'][i]
            else:
                powerAvailable += generation['Lim MW'][i]
                energyAvailable += generation['Lim MW'][i] * r


    if energyAvailable >= energyNeeded and powerAvailable >= peakPowerNeeded:
        return 0
    elif energyNeeded == 0:
        return 0
    elif energyNeeded > 0 and powerAvailable >= peakPowerNeeded:
        u = (r - (r*(energyAvailable/energyNeeded)))
        return min(r, u + s)
    else:
        return 0
    '''



def distributedGenerationNoPeak(loads, generationData, connection, r, s):


    energyStorage = 0
    energyNeeded = 0
    for i in connection:
        if i in generationData.index:
            if generationData['Lim MW'][i] > 0 and generationData['E cap'][i] == 0:
                energyNeeded -= generationData['Lim MW'][i] * (r-s)
            elif generationData['Lim MW'][i] > 0 and generationData['E cap'][i] > 0:
                energyStorage += generationData['E cap'][i]
        if i in loads.index:
            #print('i in loads.index', i)
            energyNeeded += loads['Load level average [MW]'][i] * (r-s)

    #print('powerNeded', powerNeded)
    #print('energyNeeded', energyNeeded)
    #print('powerAvailable', powerAvailable)
    #print('energyAvailable', energyAvailable)


    if energyNeeded <= 0:
        return 0
    if energyStorage > energyNeeded:
        return 0
    else:
        u = (r-s) - (r-s)*(energyStorage/energyNeeded)
        return min(r, u+s)




def loadCurveDistributedGenerationNoPeak(energyNeeded, generationData, connection, r, s):

    energyStorage = 0
    energyNeeded = 0
    for i in connection:
        if i in generationData.index:
            if generationData['Lim MW'][i] > 0 and generationData['E cap'][i] == 0:
                energyNeeded -= generationData['Lim MW'][i] * (r-s)
            elif generationData['Lim MW'][i] > 0 and generationData['E cap'][i] > 0:
                energyStorage += generationData['E cap'][i]


    #print('powerNeded', powerNeded)
    #print('energyNeeded', energyNeeded)
    #print('powerAvailable', powerAvailable)
    #print('energyAvailable', energyAvailable)


    if energyNeeded <= 0:
        return 0
    if energyStorage > energyNeeded:
        return 0
    else:
        u = (r-s) - (r-s)*(energyStorage/energyNeeded)
        return min(r, u+s)





    '''
    for i in connection:
        if i in generation.index:
            if generation['E cap'][i] > 0:
                powerAvailable += generation['Lim MW'][i]
                energyAvailable += generation['E cap'][i]
            else:
                powerAvailable += generation['Lim MW'][i]
                energyAvailable += generation['Lim MW'][i] * r


    if energyAvailable >= energyNeeded and powerAvailable >= peakPowerNeeded:
        return 0
    elif energyNeeded == 0:
        return 0
    elif energyNeeded > 0 and powerAvailable >= peakPowerNeeded:
        u = (r - (r*(energyAvailable/energyNeeded)))
        return min(r, u + s)
    else:
        return 0
    '''





#this PV function is not fully implemented, but is an example of how the PV function from Enevoldsen2021 would be coded
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
        