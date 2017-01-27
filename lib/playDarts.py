#Program takes in a spectrum and information on the binning.  The code
#Then plays darts, picking random numbers on the spectrum's defined
#region.  If the number shot is below the spectrum, Store it in an array as
#an event.  When the number of events requested is collected, build the
#Experiment's histogram.

import numpy as np

def RandShoot(mu, sigma,n):
    '''
    Returns an array of n numbers from a gaussian distribution of
    average mu and variance sigma. If less than zero, return zero.
    '''
    result = mu + sigma * np.random.randn(n)
    for num in result:
        if num < 0.0:
            num = 0
    return result

