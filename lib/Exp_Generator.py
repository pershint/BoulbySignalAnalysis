import copy
import matplotlib.pyplot as plt
import playDarts as pd
import numpy as np

DEBUG = False

#Class takes in a signal class as defined in DBParse.py and creates the spectrum
#For an experiment.
class ExperimentGenerator(object):
    def __init__(self,signalClass, schedule_dict, resolution, cores):
        self.signals = signalClass.signals
        
        self.offtime = schedule_dict["OFF_TIME"]
        self.uptime = schedule_dict["UP_TIME"]
        self.totaldays = schedule_dict["TOTAL_RUN"]
        self.killreacs = schedule_dict["KILL_CORES"]
        self.killdays = schedule_dict["KILL_DAYS"]
        self.ufirstoffs = schedule_dict["FIRST_UNKNOWNSHUTDOWNS"]
        self.kfirstoffs = schedule_dict["FIRST_KNOWNSHUTDOWNS"]
        self.minterval = schedule_dict["MAINTENANCE_INTERVAL"]
        self.mtime = schedule_dict["MAINTENANCE_TIME"]
        self.undecstarts = schedule_dict["UNDECLARED_OUTAGE_STARTS"]
        self.undecdays = schedule_dict["UNDECLARED_OUTAGE_LENGTHS"]
        self.undeccore = schedule_dict["UNDECLARED_OUTAGE_CORE"]
        self.coredict = cores
        self.numcores = len(cores["known_cores"]) + len(cores["unknown_cores"])
        self.numknowncores = len(cores["known_cores"])
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
        self.known_core_events = {} #IBDs/day generated for known core
        self.known_core_binavg = 0  #Sum of avg. IBDs/day for all known cores
        self.unknown_core_events = {} #IBDs/day generated for unknown core
        self.unknown_core_binavg = 0 #Sum of avg. IBDs/day for all unknown cores
        self.generateCoreEvents()

        #Now, build the day by day event rate if all cores never shut off
        self.events_allcoreson = copy.deepcopy(self.NR_bkg)
        for core in self.coredict["known_cores"]:
            self.events_allcoreson += self.known_core_events[core]
        if self.areunknowns:
            for core in self.coredict["unknown_cores"]:
                self.events_allcoreson += self.unknown_core_events[core]
        #Define the scheduled days for each core in the experiment to 
        #Turn off for a long outage or a short maintenance period
        self.core_shutoff_startdays = {}
        self.core_maintenance_startdays = {}
        self.core_opmap = {}
        self.BuildShutdownMaintSchedules()

        #With the schedule constructed, build a day-by-day map of how many
        #Cores are on or off for a given day
        self.known_numcoreson = np.zeros(self.totaldays) # of cores on/day
        self.unknown_numcoreson = np.zeros(self.totaldays) # of cores on/day
        self.BuildNumCoresOnMaps()

        #Use the outage schedule to remove events based on when cores are off
        self.removeDeclaredOutageEvents()

        #Now, if there's an undeclared outage, strip the events from that core
        self.undeclared_daysoff = np.zeros(self.totaldays) #1 if off, 0 if on
        self.removeUndeclaredOutageEvents()

        #Define core_status_array, which tells you the total number of
        #known reactors on in a given day, and the final #events/day for the
        #whole experiment with outages included.
        self.core_status_array = copy.deepcopy(self.known_numcoreson)
        self.events = copy.deepcopy(self.NR_bkg)
        for core in self.coredict["known_cores"]:
            self.events += self.known_core_events[core]
        if self.areunknowns:
            for core in self.coredict["unknown_cores"]:
                self.events += self.unknown_core_events[core]
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
    def stripSDDays(self,core_events, killday):
        for j,day in enumerate(self.experiment_days):
            if self.experiment_days[j] > killday:
                #set events in that bin to zero
                core_events[j] = 0.0
        return core_events

    #Generates core events for known core (reactor background) and unknown core
    #DOES NOT assume shut-offs occur.
    def generateCoreEvents(self):
        #average events/day (binavg) arrays and random shoot events/day
        core_signal_dict = {}
        core_binavg_dict = {}
        for signal in self.signals:
            if signal in self.allcores:
                core_binavg = self.signals[signal]
                core_events = pd.RandShoot_p(core_binavg, self.totaldays)
                for j, killcore in enumerate(self.killreacs):
                    if signal==killcore:
                        core_events = self.stripSDDays(core_events,self.killdays[j])
                core_signal_dict[signal] = core_events
                core_binavg_dict[signal] = core_binavg
        #Place the values into their proper class containers
        for core in core_signal_dict:
            if core in self.coredict["known_cores"]:
                self.known_core_events[core] = core_signal_dict[core]
                self.known_core_binavg += core_binavg_dict[core]
            elif core in self.coredict["unknown_cores"]:
                self.unknown_core_events[core] = core_signal_dict[core]
                self.unknown_core_binavg += core_binavg_dict[core]

    def BuildShutdownMaintSchedules(self):
        '''
        Builds the schedules used to remove events according to when
        A core shuts off for a long outage or a maintenance period.
        '''
        #generate the days that each reactor shuts off
        core_shutoffs = {}
        for j,corename in enumerate(self.coredict["known_cores"]):
            core_shutoffs[corename] = []
            shutoff_day = self.kfirstoffs[j]
            core_shutoffs[corename].append(shutoff_day)
            while ((shutoff_day +self.offtime+ self.uptime) < self.totaldays):
                shutoff_day = (shutoff_day + self.offtime) + self.uptime
                core_shutoffs[corename].append(shutoff_day)
        for j,corename in enumerate(self.coredict["unknown_cores"]):
            core_shutoffs[corename] = []
            shutoff_day = self.ufirstoffs[j]
            core_shutoffs[corename].append(shutoff_day)
            while ((shutoff_day +self.offtime+ self.uptime) < self.totaldays):
                shutoff_day = (shutoff_day + self.offtime) + self.uptime
                core_shutoffs[corename].append(shutoff_day)
        self.core_shutoff_startdays = core_shutoffs
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

        self.core_maintenance_startdays = core_maintenances

    def BuildNumCoresOnMaps(self):
        '''
        Generate a day-by-day map of the core states for the known
        and unknown reactors defined.
        Also generates the list showing what kind of outage occured on
        the day.
        0 - all cores off, 1 - one core on, 2 - two cores on, etc.
        '''
        for core in self.core_shutoff_startdays:
            onoffdays = np.ones(self.totaldays)
            offtype = ["n/a"]*self.totaldays
            #first, identify off days associated with maintenance periods
            if self.minterval is not None:
                for maintenance_day in self.core_maintenance_startdays[core]:
                    j = maintenance_day - 1
                    while j < ((maintenance_day - 1) + self.mtime):
                        if(j == self.totaldays):
                            break
                        onoffdays[j] = 0
                        offtype[j] = "M"
                        j+=1
            #Now, identify off days associated with big shutdowns
            for shutdown_day in self.core_shutoff_startdays[core]:
                j = shutdown_day - 1
                while j < ((shutdown_day - 1) + self.offtime):
                    if(j == self.totaldays):
                        break
                    onoffdays[j] = 0
                    offtype[j] = "S"
                    j+=1
            #if this core has a permanent shutdown, set it's status to zero
            for j, killcore in enumerate(self.killreacs):
                if core==killcore:
                    onoffdays[self.killdays[j]:self.totaldays] = 0
                    offtype[self.killdays[j]:self.totaldays] = \
                    ["K"] * ((self.totaldays - self.killdays[j])+1)
            #Add this core's schedule map to the full reactor outage map
            self.core_opmap[core] = offtype
            if core in self.coredict["known_cores"]:
                self.known_numcoreson += onoffdays
            elif core in self.coredict["unknown_cores"]:
                self.unknown_numcoreson += onoffdays


    def removeDeclaredOutageEvents(self):
        '''
        Code defines the first shutoff days for each reactor.  Then,
        goes through the experiment, bin by bin, and re-shoots a value
        for each bin with the average scaled by how many days the reactor
        was off for that bin.
        '''
        #Now, go through each bin of core data and remove the appropriate
        #portion of reactor flux for the shutoff
        #FIXME: There's optimization to be done here for sure
        for core in self.core_shutoff_startdays:
            for shutdown_day in self.core_shutoff_startdays[core]:
                OT_complete = False
                for j,day in enumerate(self.experiment_days):
                    #If a shutdown happened, set the IBD events for days
                    #During the shutdown to zero for the core
                    if ((shutdown_day + self.offtime) <= day):
                            OT_complete = True
                    elif shutdown_day <= day:
                        if core in self.coredict["known_cores"]:
                            self.known_core_events[core][j] = 0.0
                        elif core in self.coredict["unknown_cores"]:
                            self.unknown_core_events[core][j] = 0.0
                    if OT_complete:
                        break
            if self.minterval is not None:
                for maintenance_day in self.core_maintenance_startdays[core]:
                       MT_complete = False
                       for j,day in enumerate(self.experiment_days):
                           #If a maintenance happened, set the IBD events for days
                           #During the shutdown to zero for the core
                           if ((maintenance_day + self.mtime) <= day):
                                   MT_complete = True
                           elif maintenance_day <= day:
                               if core in self.coredict["known_cores"]:
                                   self.known_core_events[core][j] = 0.0
                               elif core in self.coredict["unknown_cores"]:
                                   self.unknown_core_events[core][j] = 0.0
                           if MT_complete:
                               break

    def removeUndeclaredOutageEvents(self):
        '''
        Code defines the first shutoff days for each reactor.  Then,
        goes through the experiment, bin by bin, and re-shoots a value
        for each bin with the average scaled by how many days the reactor
        was off for that bin.
        '''
        for outage in self.undecstarts:
            #Build your undeclared map of 0's and 1's first
            print("THE DREAM")

    def show(self):
        print("Average Non-Reactor background events per division: " + \
                str(self.avg_NRbackground))
        print("Background array: \n" + str(self.NR_bkg))
        print("day of experiment array: \n" + str(self.experiment_days))
        print("#Cores on for a day: \n" + str(self.core_status_array))

