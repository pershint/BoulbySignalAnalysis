import playDarts as pd
import numpy as np

#Class takes in a signal class as defined in DBParse.py and creates the spectrum
#For an experiment.
class ExperimentGenerator(object):
    def __init__(self,signalClass, offtime, uptime, resolution, unknown_core, totaldays):
        self.signals = signalClass.signals
        self.efficiency = signalClass.efficiency
        self.offtime = offtime
        self.uptime = uptime
        self.totaldays = totaldays
        self.resolution = resolution
        self.unknown_core = unknown_core
        self.numcycles = self.totaldays / self.resolution #Number of resolution periods measured
        self.experiment_days = np.arange(1*self.resolution,(self.numcycles+1)* \
                self.resolution, self.resolution)

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
        '''
        Code first generates a random on/off cycle for each core.  Then,
        goes through the experiment, day by day, and adjusts each reactor core's
        signal according to if the reactor is on or off.
        '''
        #generate the days that each reactor shuts off
        core_shutoffs = {'Core_1': [], 'Core_2': []}
        for core in core_shutoffs:
            shutoff_day = np.random.randint(1, self.uptime) #first shutoff
            core_shutoffs[core].append(shutoff_day)
            while ((shutoff_day + self.uptime) < (self.totaldays - self.offtime)):
                shutoff_day += self.uptime
                core_shutoffs[core].append(shutoff_day)
        print(core_shutoffs)        
        #Now, go through each bin of core data and remove the appropriate
        #portion of reactor flux for the shutoff

        for core in core_shutoffs:
            if core == self.unknown_core:
                for shutdown_day in core_shutoffs[core]:
                    for j,daybin in enumerate(self.experiment_days):
                        #check if shutdown time ended in this daybin
                        if ((shutdown_day + self.offtime) < daybin):
                            ondays_inbin = daybin - (shutdown_day + self.offtime)
                            self.unknown_core_events[j] = (self.unknown_core_events[j] * \
                                    (float(ondays_inbin) / float(self.resolution)))
                            break
                        elif shutdown_day < daybin:
                            dayson_inbin = self.resolution - (daybin - shutdown_day)
                            if dayson_inbin > 0:
                                self.unknown_core_events[j] = (self.unknown_core_events[j] * \
                                    (float(dayson_inbin) / float(self.resolution)))
                            else:
                                self.unknown_core_events[j] = 0
            else:
                for shutdown_day in core_shutoffs[core]:
                    for j,daybin in enumerate(self.experiment_days):
                        #check if shutdown time ended in this daybin
                        if ((shutdown_day + self.offtime) < daybin):
                            ondays_inbin = daybin - (shutdown_day + self.offtime)
                            self.known_core_events[j] = (self.known_core_events[j] * \
                                    (float(ondays_inbin) / float(self.resolution)))
                            break
                        elif shutdown_day < daybin:
                            dayson_inbin = self.resolution - (daybin - shutdown_day)
                            if dayson_inbin > 0:
                                self.known_core_events[j] = (self.known_core_events[j] * \
                                    (float(dayson_inbin) / float(self.resolution)))

    def show(self):
        print("Average Non-Reactor background events per division: " + \
                str(self.avg_NRbackground))
        print("Background array: \n" + str(self.NR_bkg))
        print("day of experiment array: \n" + str(self.experiment_days))

