import copy
import playDarts as pd
import numpy as np

DEBUG = False

#Class takes in a signal class as defined in DBParse.py and creates the spectrum
#For an experiment.
class ExperimentGenerator(object):
    def __init__(self,signalClass, schedule_dict, resolution, cores):
        self.signals = signalClass.signals
        ##self.efficiency = signalClass.efficiency
        self.offtime = schedule_dict["OFF_TIME"]
        self.uptime = schedule_dict["UP_TIME"]
        self.totaldays = schedule_dict["TOTAL_RUN"]
        self.killreacs = schedule_dict["KILL_DAY"]
        self.ufirstoff = schedule_dict["FIRST_UNKNOWNSHUTDOWN"]
        self.kfirstoff = schedule_dict["FIRST_KNOWNSHUTDOWN"]
        self.minterval = schedule_dict["MAINTENANCE_INTERVAL"]
        self.mtime = schedule_dict["MAINTENANCE_TIME"]
        self.coredict = cores
        self.numcores = len(cores["known_cores"]) + len(cores["unknown_cores"])
        self.allcores = self.parsecores()
        self.areunknowns = False
        if self.coredict["unknown_cores"]:
            self.areunknowns = True
        self.experiment_days = np.arange(1,self.totaldays+1,1)

        #Generate non-reactor background IBD candidates for each expt. day
        self.avg_NRbackground = -9999 #In events/resolution width
        self.NR_bkg = [] #Array with experiments' NR backgrounds for each day
        self.NR_bkg_unc = [] #Uncertainty bar width for each background entry
        self.generateNRBKG() #Fills above arrays using DB

        #Generate core events as if reacs are always on for each expt. day
        self.known_core_events = [] #IBDs/day generated for known core
        self.known_core_binavg = -9999
        self.unknown_core_events = [] #IBDs/day generated for unknown core
        self.unknown_core_binavg = -9999
        self.generateCoreEvents()
        self.events_allcoreson = self.NR_bkg + self.known_core_events
        if self.areunknowns:
            self.events_allcoreson += self.unknown_core_events
    
        self.known_numcoreson = np.zeros(self.totaldays) # of cores on/day
        self.unknown_numcoreson = np.zeros(self.totaldays) # of cores on/day
        self.shutoff_startdays = {}
        self.maintenance_startdays = {}
        #Now, remove events based on days a core is off
        self.removeCoreOffEvents()
        self.core_status_array = copy.deepcopy(self.known_numcoreson)
        self.events = self.NR_bkg + self.known_core_events 
        if self.areunknowns:
            self.core_status_array +=self.unknown_numcoreson
            self.events += self.unknown_core_events
        self.events_unc = np.sqrt(self.events)

        #Define your experiment_days and events, but rebinned as requested
        self.resolution = resolution
        self.numbins = self.totaldays / self.resolution #Number of resolution periods measured
        self.rb_experiment_days = np.arange(1*self.resolution,(self.numbins+1)* \
                self.resolution, self.resolution)
        #FIXME: Need to write a function to collapse event binning

    #Returns a list of all cores from the given core dictionary       
    def parsecores(self):
        corelist = []
        kcs = self.coredict["known_cores"]
        for kc in kcs:
            corelist.append(kc)
        ukcs = self.coredict["unknown_cores"]
        for ukc in ukcs:
            corelist.append(ukc)
        return corelist

    #Generates non-reactor backgrounds
    def generateNRBKG(self):
        bkg_signal_dict = {}
        avg_NRbackground = 0. #In events/day
        #Fire average events for each non-reactor BKG signal for each day
        for signal in self.signals:
            if signal not in self.allcores:
                avg_events = self.signals[signal]
                avg_NRbackground = avg_NRbackground + avg_events
                events = pd.RandShoot_p(avg_events, self.totaldays)
                bkg_signal_dict[signal] = events
        self.avg_NRbackground = avg_NRbackground
        self.NR_bkg = [] #clear out NR_bkg if already filled previously
        self.NR_bkg_unc = []
        for bkg_signal in bkg_signal_dict:
            self.NR_bkg.append(bkg_signal_dict[bkg_signal])
        self.NR_bkg = np.sum(self.NR_bkg, axis=0)
        self.NR_bkg_unc = np.sqrt(self.NR_bkg)

    #Takes in a set of binned events and removes all events past
    #The day at which reactors are scheduled for permanent shutdown
    def stripSDDays(self,binned_events):
        for j,day in enumerate(self.experiment_days):
            if self.experiment_days[j] > self.killreacs:
                #set events in that bin to zero
                binned_events[j] = 0.0
        return binned_events

    #Generates core events for known core (reactor background) and unknown core
    #DOES NOT assume shut-offs occur.
    def generateCoreEvents(self):
        core_signal_dict = {}
        core_binavg_dict = {}
        for signal in self.signals:
            if signal in self.allcores:
                core_binavg = self.signals[signal]
                binned_events = pd.RandShoot_p(core_binavg, self.totaldays)
                if self.killreacs != None:
                    binned_events = self.stripSDDays(binned_events)
                core_signal_dict[signal] = binned_events
                core_binavg_dict[signal] = core_binavg
        for core in core_signal_dict:
            if core in self.coredict["known_cores"]:
                self.known_core_events = core_signal_dict[core]
                self.known_core_binavg = core_binavg_dict[core]
            elif core in self.coredict["unknown_cores"]:
                self.unknown_core_events = core_signal_dict[core]
                self.unknown_core_binavg = core_binavg_dict[core]

    def removeCoreOffEvents(self):
        '''
        Code defines the first shutoff days for each reactor.  Then,
        goes through the experiment, bin by bin, and re-shoots a value
        for each bin with the average scaled by how many days the reactor
        was off for that bin.
        '''
        #generate the days that each reactor shuts off
        core_shutoffs = {}
        for corename in self.allcores:
            core_shutoffs[corename] = []
        for core in core_shutoffs:
            if core in self.coredict["known_cores"]:
                shutoff_day = self.kfirstoff
            elif core in self.coredict["unknown_cores"]:
                shutoff_day = self.ufirstoff
            core_shutoffs[core].append(shutoff_day)
            while ((shutoff_day +self.offtime+ self.uptime) < self.totaldays):
                shutoff_day = (shutoff_day + self.offtime) + self.uptime
                core_shutoffs[core].append(shutoff_day)
        self.shutoff_startdays = core_shutoffs
        #Take the core shutoff days and build a maintenance schedule
        #That will be built and used in generating the day-by-day map
        core_maintenances = {}
        if self.minterval is not None:
            for corename in self.allcores:
                core_maintenances[corename] = []
            for core in core_maintenances:
                if core_shutoffs[core][0] > self.minterval:
                    #Need to add maintenance periods prior to first shutdown
                    first_maints = core_shutoffs[core][0] - self.minterval
                    while first_maints > 0:
                        core_maintenances[core].append(first_maints)
                        first_maints = first_maints - (self.mtime + self.minterval)
                #Now, make a list of maintenance starts following shutdowns
                for j, turnoffday in enumerate(core_shutoffs[core]):
                    maint_day = turnoffday + self.offtime + self.minterval
                    if (j+1) == len(core_shutoffs[core]):
                        while maint_day < self.totaldays:
                            core_maintenances[core].append(maint_day)
                            maint_day += (self.mtime + self.minterval)
                    else:
                        while maint_day < (core_shutoffs[core][j+1]):
                            core_maintenances[core].append(maint_day)
                            maint_day += (self.mtime + self.minterval)

        self.maintenance_startdays = core_maintenances

        #Generate a day-by-day map of each reactor's state
        #0 - all cores off, 1 - one core on, 2 - two cores on, etc.
        for core in core_shutoffs:
            onoffdays = np.ones(self.totaldays)
            #first, identify off days associated with big shutdowns
            for shutdown_day in core_shutoffs[core]:
                j = shutdown_day - 1
                while j < ((shutdown_day - 1) + self.offtime):
                    if(j == self.totaldays):
                        break
                    onoffdays[j] = 0
                    j+=1
            #now, identify off days associated with maintenance periods
            if self.minterval is not None:
                for maintenance_day in core_maintenances[core]:
                    j = maintenance_day - 1
                    while j < ((maintenance_day - 1) + self.mtime):
                        if(j == self.totaldays):
                            break
                        onoffdays[j] = 0
                        j+=1
            #Add this core's schedule map to the full reactor outage map
            if core in self.coredict["known_cores"]:
                self.known_numcoreson += onoffdays
            elif core in self.coredict["unknown_cores"]:
                self.unknown_numcoreson += onoffdays
        #if there's a permanent shutdown of all reactors, turn all
        #onoffdays to zero past that day
        if self.killreacs != None:
            self.known_core_numcoreson[self.killreacs:self.totaldays] = 0
            self.unknown_core_numcoreson[self.killreacs:self.totaldays] = 0

        #Now, go through each bin of core data and remove the appropriate
        #portion of reactor flux for the shutoff
        #FIXME: There's optimization to be done here for sure
        for core in core_shutoffs:
            for shutdown_day in core_shutoffs[core]:
                OT_complete = False
                for j,day in enumerate(self.experiment_days):
                    #If a shutdown happened, set the IBD events for days
                    #During the shutdown to zero for the core
                    if ((shutdown_day + self.offtime) <= day):
                            OT_complete = True
                    elif shutdown_day <= day:
                        if core in self.coredict["known_cores"]:
                            self.known_core_events[j] = 0.0
                        elif core in self.coredict["unknown_cores"]:
                            self.unknown_core_events[j] = 0.0
                    if OT_complete:
                        break
            if self.minterval is not None:
                for maintenance_day in core_maintenances[core]:
                       MT_complete = False
                       for j,day in enumerate(self.experiment_days):
                           #If a maintenance happened, set the IBD events for days
                           #During the shutdown to zero for the core
                           if ((maintenance_day + self.mtime) <= day):
                                   MT_complete = True
                           elif maintenance_day <= day:
                               if core in self.coredict["known_cores"]:
                                   self.known_core_events[j] = 0.0
                               elif core in self.coredict["unknown_cores"]:
                                   self.unknown_core_events[j] = 0.0
                           if MT_complete:
                               break

    def show(self):
        print("Average Non-Reactor background events per division: " + \
                str(self.avg_NRbackground))
        print("Background array: \n" + str(self.NR_bkg))
        print("day of experiment array: \n" + str(self.experiment_days))
        print("#Cores on for a day: \n" + str(self.core_status_array))

