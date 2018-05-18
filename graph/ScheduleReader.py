import numpy as np

class ScheduleBuilder(object):
    '''Class takes in a schedule dictionary contained in the output 
    from running the various SignalAnalyses.  Can return different features
    that are built in the ExperimentGenerator class'''
    def __init__(self, schedule_dict,core_dict=None):
        self.schedule_dict = schedule_dict
        if core_dict is None:
            self.coredict = schedule_dict["CORETYPES"]
        else:
            self.coredict = core_dict
        self.allcores = self.parsecores()
        self.uptime = schedule_dict["UP_TIME"]
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
        
        try:
            self.core_shutoff_startdays = schedule_dict["SHUTDOWN_STARTDAYS"]
            self.core_maintenance_startdays = schedule_dict["MAINTENANCE_STARTDAYS"]
        except KeyError:
            self.core_shutoff_startdays = {}
            self.core_maintenance_startdays = {}
            self.BuildShutdownMaintSchedules()


    def parsecores(self):
        corelist = []
        kcs = self.coredict["known_cores"]
        for kc in kcs:
            corelist.append(kc)
        ukcs = self.coredict["unknown_cores"]
        for ukc in ukcs:
            corelist.append(ukc)
        return corelist

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

    def BuildCoresOnMap(self,known=True):
        '''
        Generate a day-by-day map of the core states for the known
        and unknown reactors defined.
        0 - all cores off, 1 - one core on, 2 - two cores on, etc.
        '''
        OperationMap = np.zeros(self.totaldays)
        for core in self.core_shutoff_startdays:
            onoffdays = np.ones(self.totaldays)
            #first, identify off days associated with big shutdowns
            for shutdown_day in self.core_shutoff_startdays[core]:
                j = shutdown_day - 1
                while j < ((shutdown_day - 1) + self.offtime):
                    if(j == self.totaldays):
                        break
                    onoffdays[j] = 0
                    j+=1
            #now, identify off days associated with maintenance periods
            if self.minterval is not None:
                for maintenance_day in self.core_maintenance_startdays[core]:
                    j = maintenance_day - 1
                    while j < ((maintenance_day - 1) + self.mtime):
                        if(j == self.totaldays):
                            break
                        onoffdays[j] = 0
                        j+=1
            #if this core has a permanent shutdown, set it's status to zero
            for j, killcore in enumerate(self.killreacs):
                if core==killcore:
                    onoffdays[self.killdays[j]:self.totaldays] = 0
            #Add this core's schedule map to the full reactor outage map
            if known is True:
                if core in self.coredict["known_cores"]:
                    OperationMap += onoffdays
            else:
                if core in self.coredict["unknown_cores"]:
                    OperationMap += onoffday
        return OperationMap

