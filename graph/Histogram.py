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

def hPlot_Determ(evperdays, numbins, hmin, hmax):
    '''
    Takes the signal name, and an array of randomly shot events per day, and
    outputs the histogram for the events fired.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.hist(evperdays, numbins, facecolor='blue', alpha=0.75)
    ax.set_title("# Days of 'one reactor off' data needed for mesaurement")
    ax.set_xlabel("# Days of off-core data")
    ax.set_ylabel("# Experiments")
    ax.set_xbound(lower=hmin,upper=hmax)
    ax.grid(True)
    plt.show()

def hPlot_Determ_InExpDays(evperdays, numbins, hmin, hmax):
    '''
    Takes the signal name, and an array of randomly shot events per day, and
    outputs the histogram for the events fired.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.hist(evperdays, numbins, facecolor='m', alpha=0.75)
    ax.set_title("# Experiental Days needed for on/off measurement")
    ax.set_xlabel("# Days in experiment")
    ax.set_ylabel("# Experiments")
    ax.set_xbound(lower=hmin,upper=hmax)
    ax.grid(True)
    plt.show()

def hPlot_CoresOnAndOffHist(GenExp):
    '''
    Takes in an ExperimentGenerator class and gives the event distribution
    for the selected binning (nbins below) for if all cores stayed on in
    #an experiment, and if both cores had shutoff periods.
    '''
    fig = plt.figure()
    nbins = 15
    xmin=np.min([np.min(GenExp.events_allcoreson),np.min(GenExp.events)])-1
    xmax=np.max([np.max(GenExp.events_allcoreson),np.max(GenExp.events)])+1
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)
    ax1.hist(GenExp.events_allcoreson, nbins, facecolor = 'blue', alpha=0.75)
    ax1.set_title("Histogram of events per bin distribution \n" + \
            "[NR backgrounds + both cores on]")
    ax1.set_xbound(lower=xmin, upper=xmax)
    ax1.set_xlabel("Candidate Events")
    ax1.set_ylabel("# Bins")
    ax2_xmin = np.min(GenExp.events) - 1
    ax2_xmax = np.max(GenExp.events) + 1
    ax2_nbins = int((ax2_xmax - ax2_xmin) / 4)
    ax2.hist(GenExp.events, nbins, facecolor = 'blue', alpha=0.75)
    ax2.set_xbound(lower=xmin,upper=xmax)
    ax2.set_title("Histogram of events per bin distribution \n" + \
            "[NR backgrounds + cores do shut off]")
    ax2.set_xlabel("Candidate Events")
    ax2.set_ylabel("# Bins")
    plt.show()
