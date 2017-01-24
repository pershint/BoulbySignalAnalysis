import numpy as np
import matplotlib.pyplot as plt

#Simple histogram object: holds an array of bin values, array of bin centers on
#the x-axis, and arrays of the left and right values for each bin's edges
class Histogram(object):
    def __init__(self, bin_values, bin_centers, bin_lefts, bin_rights):
        #Initialize arrays that hold bin end locations
        self.bin_lefts = bin_lefts
        self.bin_rights = bin_rights
        #initialize array for each bin's center value
        self.bin_centers = bin_centers
        #initialize array to hold the bin's value
        self.bin_values = bin_values
        #initialize value that tells you the bin width in x-axis units
        self.bin_width = self.bin_rights[0] - self.bin_lefts[0]

def Plot_SignalHistogram(signal_name, evperdays, numbins, hmin, hmax):
    '''
    Takes the signal name, and an array of randomly shot events per day, and
    outputs the histogram for the events fired.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.hist(evperdays, numbins, facecolor='blue', alpha=0.75)
    ax.set_title("Histogram for " + str(signal_name))
    ax.set_xbound(lower=hmin,upper=hmax)
    ax.grid(True)
    plt.show()
