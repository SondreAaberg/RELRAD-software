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
    var = 1/len(EENS)*(len(EENS)-1)*np.sum((EENS-meanEENS)**2)
    return var

def calcNumberOfSimulations(beta, EENS):
    # Calculate the number of simulations needed to achieve the desired precision

    meanEENS = np.mean(EENS)
    varEENS = var(EENS)

    n = (beta * np.sqrt(varEENS) / meanEENS) ** 2
    n = int(np.ceil(n))

    return n

   