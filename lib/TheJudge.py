class TheJudge(object):
    def __init__(self):
        print("INITIALIZING A JUDGE CLASS")
        self.PH_dist_train = []  #Array of FB-algorithm probability distributions 

class CLJudge(TheJudge):
    '''The CLJudge is a TheJudge subclass that looks at WATCHMAN data processed
    with the Forward-Backward Algorithm.  Training data is used to define the
    bands in probability space that are consistent with different types of
    reactor operation.  Can then try to identify shutdowns in test data.
    
    Currently, this judge's training only works with the following configuration, and
    thus only tries to identify reactor states for the following configuration:
        - Assumes two reactor cores to monitor
        - If a core is off, only one core is off at any time
        - Three possible states for Hartlepool: "Both On", "One off, maintenance", or
          "one off, long shutdown"
    '''

    def __init__(self): 
        super(CLJudge, self).__init__()
        #Used in training process
        self.CL = None
        self.probdistdict = None
        self.banddict = None
        self.PH_CLhi = []
        self.PH_CLlo = []

    def SetCLWidth(self,CL):
        '''Set what confidence (fraction of 1) you want the Judge to learn each
        operational type to.  For example, if CL=0.683, the Judge will learn the region 
        in FB-algorithm probability space for each reactor operational state with 68.3% coverage.'''
        self.CL = CL

    def AddTrainingDistributions(self,PH_Dist):
        '''add one or many training distributions to the list of all traning 
        distributions'''
        PHD = np.array(PH_Dist)
        if len(np.shape(PHD))==1:
            self.PH_dist_train.append(PH_Dist)
        else:
            self.PH_dist_train = self.PH_dist_train + PH_Dist

    def ClearTrainingDistributions(self):
        '''Empties the training distributions array'''
        self.PH_dist_train = []


    def TrainTheJudge(self):
        '''Using all loaded training data, finds the bands of FB algorithm output that correspond 
        to different reactor states'''
        if len(self.PH_dist_train) == 0:
            print("You must give the judge training data before training him.")
            return
        #The following two lines find the CL bands by looking at each
        #day's 90% CL bands, then averaging the band edges for each dist.
        self.PH_CLhi, self.PH_CLlo = self._FindDailyPHSpread(self.PH_dist_train)

        #The following takes days from all operation regions and puts them
        #Into their own histograms, and finds the bands there
        self.probdistdict, self.banddict = self._findOpRegions()


    def _JudgeOp(self,PHDist=None):
        '''Here, the Judge uses the trained CL bands to try and predict the state of
        the Hartlepool complex operation to within 90% accuracy, as well as
        detect deviations to within 90% accuracy.'''
        if PHDist is None:
            print("You must feed in a 'probability of being on' distribution"+\
                    "to run this prediction.")
        CLLimit = 0.80
        CLkeys = self.banddict.keys()
        Day_OpType_Candidates = {}
        for CL in CLkeys:
            Day_OpType_Candidates[CL] = []
        #Go day by day and see if the probability is consistent with any
        #of our bands
        for j,day in enumerate(self.experiment_days):
            for band in self.banddict:
                if self.banddict[band][0] < PHDist[j] < self.banddict[band][1]:
                    Day_OpType_Candidates[band].append(day)
        #Now, we'll try to reconstruct the regions of operation using the
        #Day_OpType_Candidates
        RunPredictions = {}
        days_in_window = []
        for optype in Day_OpType_Candidates:
            if optype == "both on":
                onwindow = 10 
                bothon_prediction = np.zeros(len(self.experiment_days))
                for day in Day_OpType_Candidates[optype]:
                    days_in_window.append(day)
                    #check if The total num. of events
                    allinwindow = True
                    rangeinwindow = max(days_in_window) - min(days_in_window)
                    if rangeinwindow > onwindow:
                        allinwindow = False 
                    while not allinwindow:
                        del days_in_window[0]
                        if max(days_in_window) - min(days_in_window) <= onwindow:
                            allinwindow=True
                    #If this window is filled with on days above CL, mark them
                    if (float(len(days_in_window))/onwindow) >= CLLimit:
                        bothon_prediction[min(days_in_window):max(days_in_window)]=1
                RunPredictions[optype] = list(bothon_prediction)
            elif optype == "one off, shutdown":
                offwindow = 60 
                shutdown_prediction = np.zeros(len(self.experiment_days))
                for day in Day_OpType_Candidates[optype]:
                    days_in_window.append(day)
                    #check if The total num. of events
                    allinwindow = True
                    if max(days_in_window) - min(days_in_window) > offwindow:
                        allinwindow = False 
                    while not allinwindow:
                        del days_in_window[0]
                        if max(days_in_window) - min(days_in_window) <= offwindow:
                            allinwindow=True
                    #If this window is filled with on days above CL, mark them
                    if (float(len(days_in_window))/offwindow) >= CLLimit:
                        shutdown_prediction[min(days_in_window):max(days_in_window)]=1
                RunPredictions[optype] = (list(shutdown_prediction))
            elif optype == "one off, maintenance":
                maint_prediction = np.zeros(len(self.experiment_days))
                for day in Day_OpType_Candidates[optype]:
                    days_in_window.append(day)
                    #check if The total num. of events
                    allinwindow = True
                    if max(days_in_window) - min(days_in_window) > m_offwindow:
                        allinwindow = False 
                    while not allinwindow:
                        del days_in_window[0]
                        if max(days_in_window) - min(days_in_window) <= m_offwindow:
                            allinwindow=True
                    #If this window is filled with on days above CL, mark them
                    if (float(len(days_in_window))/offwindow) >= CLLimit:
                        maint_prediction[min(days_in_window):max(days_in_window)]=1
                        days_in_window = []
                RunPredictions[optype] = list(maint_prediction)
        return Day_OpType_Candidates, RunPredictions

    def _Get_Distributions_CLCoverage(self,single_PH, nbins):
        median =np.median(single_PH)
        binedges = np.arange(0.0,1.0 + (1.1/float(nbins)), (1.0/float(nbins)))
        PH_CLhi = None
        PH_CLlo = None
        hist, binedges = np.histogram(single_PH,bins=binedges)
        #find the bin index where this average is located
        median_bin = np.where(median < binedges)[0][0]
        sumlength = np.max([median_bin, len(hist)- median_bin])
        current_CL = 0.0
        tot_entries = float(hist.sum())
        past_CL = False
        summedalllo = False
        summedallhi = False 
        for i in xrange(sumlength):
            if past_CL is True:
                outind = i
                break
            if i==0:
                current_CL += float(hist[median_bin])/ tot_entries
            else:
                #FIXME: Confirm you have overcoverage here
                if median_bin-i >= 0:
                    current_CL += float(hist[median_bin-i])/ tot_entries
                else:
                    summedalllo = True
                if median_bin+i <= len(hist)-1:
                    current_CL += float(hist[median_bin+i])/ tot_entries
                else:
                    summedallhi = True
            if current_CL >= self.CL:
                passed_CL = True
                break
        if summedallhi is True:
            PH_CLhi = (binedges[len(binedges)-1])
        else:
            PH_CLhi = (binedges[median_bin+i])
        if summedalllo is True:
            PH_CLlo = (binedges[0])
        else:
            PH_CLlo = (binedges[median_bin-i])
        return PH_CLhi, PH_CLlo

    def _FindDailyPHSpread(self,PH_dist):
        '''Given an array of FB algorithm probability distributions,
        returns two arrays that give the day-by-day upper and lower
        bound on where the probability values lie to the input CL'''
        PH_90hi = []
        PH_90lo = []
        PH_median =np.median(PH_dist,axis=0)
        for i in xrange(len(PH_dist[0])): #Gets ith index of each day
            dayprobs = []
            for e in xrange(len(PH_dist)):
                dayprobs.append(PH_dist[e][i])
            dayprobs = np.array(dayprobs)
            PH_CLhi, PH_CLlo = self._Get_Distributions_CLCoverage(dayprobs,60) 
            PH_90hi.append(PH_CLhi)
            PH_90lo.append(PH_CLlo)
        return PH_90hi, PH_90lo

    def _ErrBars_PH_Spread_FC(self,PH_dist):
        '''For the array of given PH distributions, calculate the Feldman-
        Cousins confidence limit interval where the probability curve will
        lie'''
        PH_90hi = []
        PH_90lo = []
        binwidth=(1.0/60.0)
        binedges = np.arange(0.0,1.0 + (0.9/60), binwidth)
        for i in xrange(len(PH_dist[0])): #Gets ith index of each day
            dayprobs = []
            for e in xrange(len(PH_dist)):
                dayprobs.append(PH_dist[e][i])
            dayprobs = np.array(dayprobs)
            hist, binedges = np.histogram(dayprobs,bins=binedges)
            indices = np.arange(0,len(hist),1)
            #Order the histograms from greatest to least; also order
            #the indices along the way for the cumulative sum we will do
            hist_ordered = [x for x,_,_ in sorted(zip(hist,indices,binedges))[::-1]]
            ind_ordered = [x for _,x,_ in sorted(zip(hist,indices,binedges))[::-1]]
            bin_ordered = [x for _,_,x in sorted(zip(hist,indices,binedges))[::-1]]
            #Now, we sum from greatest to least until we are over 90%CL.  We take
            #the highest and lowest index remaining in the list of ordered indices
            #and everything inbetween to get overcoverage
            current_CL = 0.0
            tot_entries = sum(hist_ordered)
            past_CL = False
            for i in xrange(tot_entries):
                current_CL += float(hist_ordered[i])/ tot_entries
                if current_CL >= self.CL:
                    past_CL is True
                    break
            #Get the max indices from ind_ordered from 0 to broke at i
            ind_inCL = ind_ordered[0:i]
            print("INDICES IN CL: " + str(ind_inCL))
            binleft = np.min(ind_inCL)
            binright = np.max(ind_inCL)
            PH_90hi.append(binedges[binright]+binwidth)
            PH_90lo.append(binedges[binleft])
        return PH_90hi, PH_90lo
    
    def _findOpRegions(self,nbins=60):
        '''Returns the high and low bands consistent with "both cores on" and
        "one core off" to the defined CL.  nbins defines the number of bins used
        building the histograms of each day's FB-algorithm probability distribution'''
        bothon_Ps = []
        oneoff_M_Ps = []
        oneoff_S_Ps = []
        #We build bothon, oneoff_S, and
        #oneoff_M region probability histograms
        #First, rebuild experiment's op map
        opmap = ["on"] * self.experiment_length 
        for core in self.core_opmaps:
            for j,dayop in enumerate(self.core_opmaps[core]):
                if dayop == "S":
                    opmap[j] = "off_s" 
                elif dayop == "M":
                    opmap[j] = "off_m"  
        #Now, for any day of each type, append
        #That day's FB probability value to that
        #data array
        for expt_PH in self.PH_dist_train:
            for j,state in enumerate(opmap):
                if state == 'on':
                    bothon_Ps.append(expt_PH[j]) 
                elif state == 'off_s':
                    oneoff_S_Ps.append(expt_PH[j]) 
                elif state == 'off_m':
                    oneoff_M_Ps.append(expt_PH[j])  
                else:
                    print("Something went wrong with defining states in your op maps...")
                    return
        bothon_hiCL,bothon_loCL = self._Get_Distributions_CLCoverage(bothon_Ps,
                nbins)
        offs_hiCL,offs_loCL = self._Get_Distributions_CLCoverage(oneoff_S_Ps,
                nbins)
        offm_hiCL,offm_loCL = self._Get_Distributions_CLCoverage(oneoff_M_Ps,
                nbins)
        probdistdict = {'both on': bothon_Ps, 'one off, shutdown': oneoff_S_Ps,
                'one off, maintenance': oneoff_M_Ps}
        banddict = {'both on': [bothon_loCL,bothon_hiCL], 'one off, shutdown': 
                [offs_loCL, offs_hiCL], 'one off, maintenance': [offm_loCL, offm_hiCL]}
        return probdistdict, banddict

