import numpy as np


def var(EENS):

    """
    calculates the varinace in EENS
    arguments:
        EENS: list of EENS values for each year
    returns:
        var: variance of EENS values
    """

    meanEENS = np.mean(EENS)

    var = np.sum((EENS-meanEENS)**2)/(len(EENS)-1)
    return var

def calcNumberOfSimulations(EENS, beta):
    # Calculate the number of simulations needed to achieve the desired precision

    meanEENS = np.mean(EENS)
    varEENS = var(EENS)

    print('meanEENS', meanEENS)
    print('varEENS', varEENS)

    n = ( np.sqrt(varEENS) / (beta * meanEENS)) ** 2
    n = int(np.ceil(n))

    return n

   