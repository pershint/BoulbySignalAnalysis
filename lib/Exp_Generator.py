import playDarts as pd

#Class takes in a signal class as defined in DBParse.py and creates the spectrum
#For an experiment.
class ExperimentGenerator(object):
    def __init__(self,signalClass, offtime, resolution, unknown_core, numcycles):
        self.signals = signalClass.signals
        self.offtime = offtime
        self.resolution = resolution
        self.unknown_core = unknown_core
        self.numcycles = numcycles #Number of resolution periods measured

        self.avg_background = 0 #In events/resolution width
        self.exp_bkg = []     #Array with experiments' backgrounds
        self.exp_bkg_unc = [] #Uncertainty bar width for each background entry
        self.generateBKGs()



    def generateBKG(self):
        bkg_signal_dict = {}
        avg_background = 0. #In events/day
        #Fire average events for each
        for signal in self.signals:
            if signal != self.unknown_core:
                avg_events = self.signals[signal]*self.resolution
                avg_background = avg_background + avg_events
                events = pd.RandShoot(avg_events, np.sqrt(avg_events), numcycles)
                bkg_signal_dict[signal] = events
        self.avg_background = avg_background
        self.exp_bkg = [] #clear out exp_bkg if already filled previously
        for bkg_signal in bkg_signal_dict:
            self.exp_bkg.append(bkg_signal_dict[bkg_signal])
        self.exp_bkg = np.sum(exp_bkg, axis=0)
        self.exp_bkg_unc = []
        self.exp_bkg_unc = np.sqrt(self.exp_bkg)



