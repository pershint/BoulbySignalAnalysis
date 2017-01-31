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

def hPlot_SignalHistogram(signal_name, evperdays, numbins, hmin, hmax):
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

def hPlot_CoresOnAndOffHist(GenExp):
    '''
    Takes in an ExperimentGenerator class and prints the histograms for
    an experiment if all cores stayed on, and if both cores had shutoff
    periods.
    '''
    fig = plt.figure()
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)
    ax1_xmin = np.min(GenExp.events_allcoreson) - 1
    ax1_xmax = np.max(GenExp.events_allcoreson) + 1
    ax1_nbins = ax1_xmax - ax1_xmin
    ax1.hist(GenExp.events_allcoreson, ax1_nbins, facecolor = 'blue', alpha=0.75)
    ax1.set_title("Histogram of events per bin distribution \n" + \
            "[NR backgrounds + both cores on]")
    ax1.set_xlabel("Candidate Events")
    ax1.set_ylabel("# Bins")
    ax2_xmin = np.min(GenExp.events) - 1
    ax2_xmax = np.max(GenExp.events) + 1
    ax2_nbins = ax2_xmax - ax2_xmin
    ax2.hist(GenExp.events, ax2_nbins, facecolor = 'blue', alpha=0.75)
    ax2.set_title("Histogram of events per bin distribution \n" + \
            "[NR backgrounds + cores do shut off]")
    ax2.set_xlabel("Candidate Events")
    ax2.set_ylabel("# Bins")
    plt.show()
