import numpy as np
import pandas as pd

def createLoadCurve(loadCurveData):
    loadCurve = []
    for t in range(1, 3737):
        week = t/(8736/52)
        day = (week-np.floor(week))*7
        hour = (day-np.floor(day))*24

        if day == 0:
            day = 7

        if hour == 0 or round(hour) == 0:
            hour = 24
        
        # Rounding to the nearest upper integer
        week = int(np.ceil(week))
        day = int(np.ceil(day))
        if (hour-np.floor(hour)) < 0.0001:
            hour = int(np.round(hour))
        else:
            hour = int(np.ceil(hour))


        if day == 6 or day == 7: #weekend
            if week >= 1 and week <= 8: # Winter
                hourlyfactor = 'Winter Wknd'
            elif week >= 9 and week <= 17: # Spring
                hourlyfactor = 'Spring/Fall Wknd'
            elif week >= 18 and week <= 30: # Summer
                hourlyfactor = 'Summer Wknd'
            elif week >= 31 and week <= 43: # Fall
                hourlyfactor = 'Spring/Fall Wknd'
            else: # Winter
                hourlyfactor = 'Winter Wknd'
        
        else: # weekday
            if week >= 1 and week <= 8: # Winter
                hourlyfactor = 'Winter Wkdy'
            elif week >= 9 and week <= 17: # Spring
                hourlyfactor = 'Spring/Fall Wkdy'
            elif week >= 18 and week <= 30: # Summer
                hourlyfactor = 'Summer Wkdy'
            elif week >= 31 and week <= 43: # Fall
                hourlyfactor = 'Spring/Fall Wkdy'
            else: # Winter
                hourlyfactor = 'Winter Wkdy'
 
        loadCurve.append(loadCurveData['weeklyFactor'].at[week, 'Load Factor']/100 * loadCurveData['dailyFactor'].at[day, 'Load Factor']/100 * loadCurveData['hourlyFactor'].at[hour, hourlyfactor]/100) # (Factors are given in %.)
    return loadCurve

def loadCurveSumEnergy(t, r, peakLoad, loadCurve):
    """
    Calculates the total energy demand of a load for a time period r strating at t using load curve.
    Arguments:
        t: time in hours since the start of the year
        r: time in hours for which the load curve is calculated
        peakLoad: peak load in MW
        loadCurveData: List containing the load curve
    Returns:
    """
    
    E = 0

    #creates a list of the length of time the load is in each of the load curve points
    # The first element is the time from t to the next full hour, the last element is the time from the last full hour to r
    timeList = []
    timeList.append(1-t%1)
    for i in range(int(np.floor(r-1-t%1))):
        timeList.append(1)
    timeList.append((r-(1-t%1))%1)

    for i in range(len(timeList)):
        timePoint = np.int(np.floor(t+i))
        E += timeList[i] * loadCurve[timePoint] * peakLoad # Energy in MWh
    return E


    
    
