import playDarts as pd
import numpy as np

#Class takes in a signal class as defined in DBParse.py and creates the spectrum
#For an experiment.
class ExperimentGenerator(object):
    def __init__(self,signalClass, offtime, resolution, unknown_core, numcycles):
        self.signals = signalClass.signals
        self.efficiency = signalClass.efficiency
        self.offtime = offtime
        self.resolution = resolution
        self.unknown_core = unknown_core
        self.numcycles = numcycles #Number of resolution periods measured
        self.experiment_day = np.arange(1*resolution,(numcycles+1)*resolution, \
                resolution)

        #First, populate non-reactor backgrounds
        self.avg_NRbackground = 0 #In events/resolution width
        self.NR_bkg = []     #Array with experiments' non-reactor backgrounds
        self.NR_bkg_unc = [] #Uncertainty bar width for each background entry
        self.generateNRBKG()

        self.known_core_events = []
        self.unknown_core_events = []
        #First, generate core events as if reactor cores were always on
        self.generateCoreEvents()
        #Now, remove events based on days a core is off
        self.removeCoreOffEvents()

        self.events = self.NR_bkg + self.known_core_events + \
                self.unknown_core_events
        self.events_unc = np.sqrt(self.events)

    #Generates non-reactor backgrounds
    def generateNRBKG(self):
        bkg_signal_dict = {}
        avg_NRbackground = 0. #In events/day
        #Fire average events for each
        for signal in self.signals:
            if signal not in ['Core_1','Core_2']:
                avg_events = self.signals[signal]*self.resolution
                avg_NRbackground = avg_NRbackground + avg_events
                events = pd.RandShoot(avg_events, np.sqrt(avg_events), self.numcycles)
                bkg_signal_dict[signal] = events
        self.avg_NRbackground = avg_NRbackground
        self.NR_bkg = [] #clear out NR_bkg if already filled previously
        for bkg_signal in bkg_signal_dict:
            self.NR_bkg.append(bkg_signal_dict[bkg_signal])
        self.NR_bkg = np.sum(self.NR_bkg, axis=0)
        self.NR_bkg_unc = []
        self.NR_bkg_unc = np.sqrt(self.NR_bkg)

    #Generates core events for known core (reactor background) and unknown core
    def generateCoreEvents(self):
        core_signal_dict = {}
        for signal in self.signals:
            if signal in ['Core_1', 'Core_2']:
                core_avg = self.signals[signal]*self.resolution
                events = pd.RandShoot(core_avg, np.sqrt(core_avg), self.numcycles)
                core_signal_dict[signal] = events
        for core in core_signal_dict:
            if core == self.unknown_core:
                self.unknown_core_events = core_signal_dict[core]
            else:
                self.known_core_events = core_signal_dict[core]

    def removeCoreOffEvents(self):
        print("Not Implemented")
        #First, shoot two random number between 0 and 3/4 the total experiment time
        #These will be the time of the first turn-off
        #Then, fire two random numbers close to ~18 months length
        #These will be (when added to the first) the second turn-off day
        #Now, have to remove events based on the date of the turn-off, and for
        #How long the reactor is off for.  Could be removing partial events from
        #bins, or all of them from a bin depending.

    def show(self):
        print("Average Non-Reactor background events per division: " + \
                str(self.avg_NRbackground))
        print("Background array: \n" + str(self.NR_bkg))
        print("day of experiment array: \n" + str(self.experiment_day))

