import playDarts as pd
import numpy as np

UNKNOWN_FIRSTOFF = 90
KNOWN_FIRSTOFF = 180

CORE_NAMES = ['Core_1', 'Core_2']

#Class takes in a generated experiment (ExperimentGenerator class) and performs
#Some Analysis assuming we know exactly the days each core is on or off
class ExperimentAnalysis1(object):
    def __init__(self, binning_choices):
        #Holds metadata of current experiment in analysis
        self.Current_Experiment = 'no current experiment'

        #Arrays that hold the event rate for each day where both
        #reactors are on or where one reactor is off
        self.onday_events = []
        self.offday_events = []

        #Rebinned data from the onday and offday event arrays above
        self.binning_choices = binning_choices
        self.binning = []
        self.binned_onday_avg = []
        self.binned_onday_stdev = []
        self.binned_offday_avg = []
        self.binned_offday_stdev = []
        self.totaldays = 'none'

        #Cumulative sum of IBD events for on days and off days
        self.csum_on = []
        self.csum_off = []
        self.csum_numdays = []

    def __call__(self, ExpGen):
        self.Current_Experiment = ExpGen
        if self.Current_Experiment.resolution != 1:
            print("Cannot perform OnOffComparison on this experiment. " + \
                    'Experiment resolution is not one day per bin. \n')
            return
        print("Run your methods for analysis")
        self.OnOffGroup(self.Current_Experiment)
        self.OnOffStats()
        for bin_choice in self.binning_choices:
            self.ReBinningStudy(bin_choice)

    def OnOffStats(self):
        '''
        Compares data from days when reactors were both on and when one reactor
        was off.  Determines how many days of data for each are needed to get a
        3sigma difference between the values.
        '''
        smallerdataset = np.min([len(self.onday_events),len(self.offday_events)])
        daysofrunning = np.arange(1,(smallerdataset+1),1)
        self.csum_numdays = daysofrunning
        determination = False
        for day in daysofrunning:
            totalondata = np.sum(self.onday_events[0:day])
            totaloffdata = np.sum(self.offday_events[0:day])
            self.csum_on.append(totalondata)
            self.csum_off.append(totaloffdata)
        #TODO: Add your analysis code checking for a 3sigma difference in data sets


    def OnOffGroup(self, ExpGen):
        '''
        Takes an experiment and groups together the days of data where
        both reactors were on, and groups days where reactor was off.
        Can only be called if ExpGen.resolution = 1.
        '''
        offday_events = []
        onday_events = []
        days_bothreacson = ExpGen.known_core_onoffdays * \
                ExpGen.unknown_core_onoffdays
        for j,day in enumerate(ExpGen.experiment_days):
            if  days_bothreacson[j] == 1:
                onday_events.append(ExpGen.events[j])
            else:
                offday_events.append(ExpGen.events[j])
        offday_events = np.array(offday_events)
        onday_events = np.array(onday_events)
        self.onday_events = onday_events
        self.offday_events = offday_events

    def ReBinningStudy(self,bin_choice):
        #if 1 < bin_choice < self.Current_Experiment.totaldays, rebin events
        if 1 < bin_choice < self.Current_Experiment.totaldays:
            rebinned_ondays, rebinned_offdays, lost_days = \
                    self.rebin_days(self.onday_events, self.offday_events, bin_choice)
            print("{0}\n,{1}\n,{2}\n".format(rebinned_ondays, \
                    rebinned_offdays, lost_days))
        #Now, calculate the average and standard deviation of each
        self.binned_onday_avg.append(np.average(rebinned_ondays))
        self.binned_onday_stdev.append(np.std(rebinned_ondays))
        self.binned_offday_avg.append(np.average(rebinned_offdays))
        self.binned_offday_stdev.append(np.std(rebinned_offdays))

        onda = (np.average(rebinned_ondays))
        ondstd = (np.std(rebinned_ondays))
        offda = (np.average(rebinned_offdays))
        offdstd = (np.std(rebinned_offdays))
       
        print("EXPIERMENT RAN FOR {} DAYS".format(self.Current_Experiment.totaldays))
        print("DAYS BOTH ON, DAYS ONE REAC OFF: {0},{1}".format(len(self.onday_events),len(self.offday_events)))
        print("BINNING OF ON/OFF DAY DATA: {0}".format(bin_choice))
        print("ON DAY AVERAGE/STDEV: {0} / {1}".format(onda, ondstd))
        print("OFF DAY AVERAGE/STDEV: {0} / {1}".format(offda, offdstd))
        print("# DAYS LOST IN REBINNING [ONDAYS, OFFDAYS]: {0}".format(lost_days))

    def rebin_days(self, onday_events, offday_events, bin_choice):
        '''
        Takes in an array of daily rates for days both reactors were on
        (onday_events) and an array of daily rates for days where one
        reactor is off (offday_events).  
        If there are any days left over not divisible by the binning increment,
        THIS DATA IS LOST.
        '''
        rebinned_ondays = []
        rebinned_offdays = []
        nonbinned_days = []
        step = 1
        event_data = {'ondays':onday_events, 'offdays':offday_events}
        for datatype in event_data:
            while (step * bin_choice) <= len(event_data[datatype]):
                rebin_datapt = np.sum(event_data[datatype][((step-1) * \
                        bin_choice):((step * bin_choice))])
                if datatype == 'ondays':
                    rebinned_ondays.append(rebin_datapt)
                elif datatype == 'offdays':
                    rebinned_offdays.append(rebin_datapt)
                step +=1
            #now, check for any data at the end that was not rebinned
            #print(event_data[datatype][((step-1)* bin_choice):((step * bin_choice))])
            lost_days = len(event_data[datatype][((step-1)* bin_choice):((step * bin_choice))])
            nonbinned_days.append(lost_days)
        return np.array(rebinned_ondays), np.array(rebinned_offdays), nonbinned_days
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

        #First, generate core events as if reactor cores were always on
        self.known_core_events = []
        self.known_core_binavg = 'none'
        self.known_core_onoffdays = []
        self.unknown_core_events = []
        self.unknown_core_binavg = 'none'
        self.unknown_core_onoffdays = []
        self.generateCoreEvents()
        self.events_allcoreson = self.NR_bkg + self.known_core_events + \
                self.unknown_core_events

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
            if signal not in CORE_NAMES:
                avg_events = self.signals[signal]*self.resolution
                avg_NRbackground = avg_NRbackground + avg_events
                events = pd.RandShoot_p(avg_events, self.numcycles)
                bkg_signal_dict[signal] = events
        self.avg_NRbackground = avg_NRbackground
        self.NR_bkg = [] #clear out NR_bkg if already filled previously
        for bkg_signal in bkg_signal_dict:
            self.NR_bkg.append(bkg_signal_dict[bkg_signal])
        self.NR_bkg = np.sum(self.NR_bkg, axis=0)
        self.NR_bkg_unc = []
        self.NR_bkg_unc = np.sqrt(self.NR_bkg)

    #Generates core events for known core (reactor background) and unknown core
    #DOES NOT assume shut-offs occur.
    def generateCoreEvents(self):
        core_signal_dict = {}
        core_binavg_dict = {}
        for signal in self.signals:
            if signal in CORE_NAMES:
                core_binavg = self.signals[signal]*float(self.resolution)
                binned_events = pd.RandShoot_p(core_binavg, self.numcycles)
                core_signal_dict[signal] = binned_events
                core_binavg_dict[signal] = core_binavg
        for core in core_signal_dict:
            if core == self.unknown_core:
                self.unknown_core_events = core_signal_dict[core]
                self.unknown_core_binavg = core_binavg_dict[core]
            else:
                self.known_core_events = core_signal_dict[core]
                self.known_core_binavg = core_binavg_dict[core]

    def removeCoreOffEvents(self):
        '''
        Code defines the first shutoff days for each reactor.  Then,
        goes through the experiment, bin by bin, and re-shoots a value
        for each bin with the average scaled by how many days the reactor
        was off for that bin.
        '''
        #generate the days that each reactor shuts off
        core_shutoffs = {'Core_1': [], 'Core_2': []}
        for core in core_shutoffs:
            if core == self.unknown_core:
                shutoff_day = UNKNOWN_FIRSTOFF
            else:
                shutoff_day = KNOWN_FIRSTOFF
            core_shutoffs[core].append(shutoff_day)
            while ((shutoff_day + self.uptime) < (self.totaldays - self.offtime)):
                shutoff_day = (shutoff_day + self.offtime) + self.uptime
                core_shutoffs[core].append(shutoff_day)
        print("CORE SHUTOFF DAYS: " + str(core_shutoffs))        

        #Generate a day-by-day map of each reactor's state (1-on, 0-off)
        for core in core_shutoffs:
            onoffdays = np.ones(self.totaldays)
            for shutdown_day in core_shutoffs[core]:
                j = shutdown_day - 1
                print("COMPARATOR TO J:" + str((shutdown_day -1) + self.offtime))
                while j < ((shutdown_day - 1) + self.offtime):
                    if(j == self.totaldays):
                        break
                    onoffdays[j] = 0.
                    j+=1
            if core == self.unknown_core:
                self.unknown_core_onoffdays = onoffdays
            else:
                self.known_core_onoffdays = onoffdays

        #Now, go through each bin of core data and remove the appropriate
        #portion of reactor flux for the shutoff

        for core in core_shutoffs:
            for shutdown_day in core_shutoffs[core]:
                OT_complete = False
                for j,daybin in enumerate(self.experiment_days):
                    flux_scaler = 1.0 #Stays 1 if no off-days in bin
                    #If a shutdown happened, scale the events according to
                    #Days on before offtime begins
                    if shutdown_day < daybin:
                        dayson_beforeOT = self.resolution - (daybin - shutdown_day)
                        if dayson_beforeOT > 0:
                            flux_scaler = (float(dayson_beforeOT) / float(self.resolution))
                        else:
                            flux_scaler = 0
                    #If a reactor started back up, add back the proper
                    #flux ratio
                    if ((shutdown_day + self.offtime) < daybin):
                            dayson_afterOT = daybin - (shutdown_day + self.offtime)
                            flux_scaler += (float(dayson_afterOT) / float(self.resolution))
                            OT_complete = True
                    #After calculating how much this bin should be scaled for
                    #This day, re-fire the bin value if re-scaled 
                    #statistics are needed
                    if flux_scaler < 1.0:
                        if core == self.unknown_core:
                            self.unknown_core_events[j] = pd.RandShoot_p((flux_scaler * self.unknown_core_binavg), 1)
                        else:
                            self.known_core_events[j] = pd.RandShoot_p( \
                                    (flux_scaler * self.known_core_binavg), 1)
                    if OT_complete:
                        break
 
    def show(self):
        print("Average Non-Reactor background events per division: " + \
                str(self.avg_NRbackground))
        print("Background array: \n" + str(self.NR_bkg))
        print("day of experiment array: \n" + str(self.experiment_days))

