import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as scs
import scipy.misc as scm

#Class takes in a generated experiment (ExperimentGenerator class) and performs
#Some Analysis assuming we know exactly the days each core is on or off
class ExperimentalAnalysis(object):
    def __init__(self):
        #Holds metadata of current experiment in analysis
        self.Current_Experiment = None

    def __call__(self, ExpGen):
        self.Current_Experiment = ExpGen

class ForwardBackwardAnalysis(ExperimentalAnalysis):
    '''This analysis uses the forward-backward algorithm to estimate
    the probability that Hartlepool's reactors are "both on" or "one off".\n\n
    Inputs on initialization:\n\n
    prob_ontooff: Probability that a transition happens from a 'both on' state
    to a 'one off' state on any given day \n
    prob_offtoon: Probability that a transition happens from a 'one off' state to
    a 'both on' state on any given day \n
    (The above two will define the Markov Chain matrix representation)\n\n
    daysperbin: Binning size for probability vector output; doesn't affect analysis
    results, only adjusts granularity for eventual plotting \n \n

    Inputs on class call:\n
    ExpGen: ExperimentGenerator class that contains a statistically generated
    WATCHMAN experiment \n
    ontototal_ratio_guess: Guess as to the ratio of on days to off days; used for
    initializing the probability vector's inputs
    '''
    
    def __init__(self,daysperbin=3):
        super(ForwardBackwardAnalysis, self).__init__()
        self.PL_distributions  = []
        self.PH_distributions = []
        self.prob_ontooff = None
        self.prob_offtoon = None
        self.experiment_length = None

    def __call__(self, ExpGen,ontototal_ratio_guess=(1140.0/1550.0),
            prob_ontooff = 26.0/1140, prob_offtoon = 26.0/410):
        '''Runs the Forward-Backward Analysis on the input ExperimentGenerator
        class and saves the predicted probabilities of being in the "both on" or
        "one off" states in self.PH_distributions and self.PL_distributions.'''

        super(ForwardBackwardAnalysis, self).__call__(ExpGen)
        self.ExpCheck()
        
        if self.experiment_length is None:
            self.experiment_length = len(self.Current_Experiment.experiment_days)
        else:
            if self.experiment_length != len(self.Current_Experiment.experiment_days):
                print("WARNING: Experiments of different lengths have been "+\
                        "loaded in/analyzed.  This could be bad if you are trying "+\
                        "to compare algorithm performance across multiple experiments")
        
        self.ontototal_ratio_guess = ontototal_ratio_guess
        self.prob_ontooff = prob_ontooff
        self.prob_offtoon = prob_offtoon
        #
        self.total_signal=0.0
        self.total_background = 0.0
        for signal in  self.Current_Experiment.signals:
            if "Core" in signal:
                self.total_signal+=self.Current_Experiment.signals[signal]
            else:
                self.total_background+=self.Current_Experiment.signals[signal]
        self._RunFB()

    def ExpCheck(self):
        if self.Current_Experiment.numcores != 2:
            print("Experiment has less or more than 2 cores..  This analysis is"+\
                    "only currently able to run with two cores currently")
            time.sleep(2)
    
    def _RunFB(self):
        '''
        Takes the statistical experiment currently loaded and
        Predicts the probability at each day whether the two neighboring
        reactors are in the "both on" or "one off" state at each day.
        '''
        #Get the experiment's events per day and day number array
        Exp_day = self.Current_Experiment.experiment_days
        Events_on_day = self.Current_Experiment.events
        
        #Initialize day "zero" of the experiment's probabilities as
        #The ratio of "one off"/total and "both on"/total expected
        PL_days = 1.0-self.ontototal_ratio_guess
        PH_days = self.ontototal_ratio_guess
        pivec = [PH_days, PL_days]
        
        #Matrix that propagates our posterior PDF at day N to the prior PDF
        #at day N+1
        a = self.prob_offtoon
        b = self.prob_ontooff
        propagator = np.array([[(1.0-b),a],[b,(1.0-a)]])
        #Calculate the forward terms
        PH_forward, PL_forward = self._calcforwardterms(propagator=propagator,
                days=Exp_day, events=Events_on_day, pivec=pivec)
        #Calculate the backward terms
        PH_backward, PL_backward = self._calcbackwardterms(propagator=propagator,
                days=Exp_day, events=Events_on_day, pivec=pivec)
        #Get the normalization factor for our final probability vector elements
        k = 1.0 / ((PH_forward*PH_backward) + (PL_forward*PL_backward))
        #Get the unnormalized Probability vectors
        PH_vec = k*PH_forward*PH_backward
        PL_vec = k*PL_forward*PL_backward
        
        #Append this experiment's results to the distributions array
        self.PL_distributions.append(PL_vec)
        self.PH_distributions.append(PH_vec)
        return

    def _calcbackwardterms(self, propagator=None, days=None, events=None, pivec=None):
        PH_backward = [1.0]
        PL_backward = [1.0]
        for j,n in reversed(list(enumerate(events))):
            #Now,we calculate the probability the event count N on the current day
            #Came from either a "both on" or "both off" state
            #FIXME: assumes cores are same signal; we can generalize this better...
            mu_L = self.total_background + (self.total_signal/2.0)
            mu_H = self.total_background + (self.total_signal)
            likelihood_off = self._poisson(mu_L, n)
            likelihood_on = self._poisson(mu_H, n)
            
            #Make an array out of our "both on" and "one off" probabilities; it's
            #Just a tool for the algorithm
            parr = np.array([[likelihood_on, likelihood_off],
                [likelihood_on, likelihood_off]])
            #Now, do the Hadamard product with the propagator (element-wise multiply)
            hmatrix = np.multiply(propagator, parr)
            
            #Finally, dot this with our most recent PL and PH backward terms
            most_recent_backwardterms = np.array([PH_backward[0],PL_backward[0]])
            this_backwardterm = np.dot(hmatrix,most_recent_backwardterms)
            #Append the newest backward term to the front of the array
            PH_backward = [this_backwardterm[0]] + PH_backward
            PL_backward = [this_backwardterm[1]] + PL_backward
        #Strip off the initialization PL and PH
        PH_backward.pop(len(PH_backward)-1)
        PL_backward.pop(len(PL_backward)-1)
        #Return the backward term matrices
        return np.array(PH_backward), np.array(PL_backward)

    def _calcforwardterms(self, propagator=None, days=None, events=None, pivec=None):
        PH_forward = [pivec[0]]
        PL_forward = [pivec[1]]
        for j,n in enumerate(events):
            #Now,we calculate the probability the event count N on the current day
            #Came from either a "both on" or "both off" state
            #FIXME: assumes cores are same signal; we can generalize this better...
            mu_L = self.total_background + (self.total_signal/2.0)
            mu_H = self.total_background + (self.total_signal)
            likelihood_off = self._poisson(mu_L, n)
            likelihood_on = self._poisson(mu_H, n)
            if j==0:
                #Initializtion step of forward calculation; no propagation matrix
                PH_forward.append(pivec[0]*likelihood_on)
                PL_forward.append(pivec[1]*likelihood_off)
                continue
            
            #First, propagate probability distributions one step foward
            posterPDF_daynm1 = np.array([[PH_forward[j]],[PL_forward[j]]])
            print("POSTPDF: " + str(posterPDF_daynm1)) 
            priorPDF_dayn = np.dot(propagator , posterPDF_daynm1)
            
            #Now, calculate the forward term. You'll notice this algorithm is
            #Very similar to the Kalman Filter; just no normalization yet
            posteriorPDF_pH =  likelihood_on * priorPDF_dayn.item(0)
            posteriorPDF_pL =  likelihood_off * priorPDF_dayn.item(1)

            #Append the probability of being low or high on this day to our arrays
            #holding each day's posterior PL and PH
            PH_forward.append(posteriorPDF_pH)
            PL_forward.append(posteriorPDF_pL)
        print("PHFORWARD: " + str(PH_forward)) 
        #Remove our "day zero" guess from algorithm return
        PH_forward.pop(0)
        PL_forward.pop(0)
        #Return the forward term matrices
        return np.array(PH_forward), np.array(PL_forward)

    def _poisson(self,mu,x):
        #TODO: If x > 100, default to a Gaussian
        return np.exp(-mu)*(mu**(x))/scm.factorial(x)

class KalmanFilterAnalysis(ExperimentalAnalysis):
    #TODO: Have prob_ontooff calculated based on input schedule
    def __init__(self, prob_ontooff = 26.0/1140, prob_offtoon = 26.0/410,daysperbin=3):
        super(KalmanFilterAnalysis, self).__init__()
        self.PL_distributions  = []
        self.PH_distributions = []
        self.prob_ontooff = prob_ontooff
        self.prob_offtoon = prob_offtoon
        self.experiment_days = []

    def __call__(self, ExpGen,ontototal_ratio_guess=(1140.0/1550.0)):
        super(KalmanFilterAnalysis, self).__call__(ExpGen)
        self.ExpCheck()
        if len(self.experiment_days) == 0:
            self.experiment_days = self.Current_Experiment.experiment_days
        else:
            if str(self.experiment_days) != str(self.Current_Experiment.experiment_days):
                print("WARNING: Experiments of different lengths have been"+\
                        "loaded in/analyzed.  I fear for you")
        self.ontototal_ratio_guess = ontototal_ratio_guess
        self.total_signal=0.0
        self.total_background = 0.0
        for signal in  self.Current_Experiment.signals:
            if "Core" in signal:
                self.total_signal+=self.Current_Experiment.signals[signal]
            else:
                self.total_background+=self.Current_Experiment.signals[signal]
        self.RunKF()

    def ExpCheck(self):
        if self.Current_Experiment.numcores != 2:
            print("Experiment has less or more than 2 cores..  This analysis is"+\
                    "only refined to run with two cores currently")
            time.sleep(2)
    
    def RunKF(self):
        '''
        Takes the statistical experiment currently loaded and
        Predicts the probability at each day whether the two neighboring
        reactors are in the "both on" or "one off" state at each day.
        '''
        #Get the experiment's events per day and day array
        Exp_day = self.Current_Experiment.experiment_days
        Events_on_day = self.Current_Experiment.events
        
        #Initialize day "zero" of the experiment's probabilities as
        #The ratio of "one off"/total and "both on"/total expected
        PL_days = [1.0-self.ontototal_ratio_guess]
        PH_days = [self.ontototal_ratio_guess]
        
        #Matrix that propagates our posterior PDF at day N to the prior PDF
        #at day N+1
        a = self.prob_offtoon
        b = self.prob_ontooff
        propagator = np.array([[(1.0-a),b],[a,(1.0-b)]])
        #Now, go day by day and run the Kalmann Filter likelihood algorithm
        for j,n in enumerate(Events_on_day):
            #First, propagate probability distributions one step foward
            posterPDF_daynm1 = np.array([[PL_days[j-1]],[PH_days[j-1]]])
            priorPDF_dayn = np.dot(propagator , posterPDF_daynm1)
            #Now,we calculate the probability the event count N on the current day
            #Came from either a "both on" or "both off" state
            #FIXME: assumes cores are same signal; we can generalize this better...
            mu_L = self.total_background + (self.total_signal/2.0)
            mu_H = self.total_background + (self.total_signal)
            likelihood_off = self._poisson(mu_L, n)
            likelihood_on = self._poisson(mu_H, n)
            #Almost ready to find the posterior PDF at the current day.  Need the
            #Correct normalization factors that will go with the following
            #Calculation to keep our posterior p_L + p_H = 1
            
            normalization = 1.0/(likelihood_off * priorPDF_dayn.item(0) + \
            likelihood_on * priorPDF_dayn.item(1))
            #Finally, calculate the posterior PDF for this day
            posteriorPDF_pL = normalization * likelihood_off * priorPDF_dayn.item(0)
            posteriorPDF_pH = normalization * likelihood_on * priorPDF_dayn.item(1)

            #Append the probability of being low or high on this day to our arrays
            #holding each day's posterior PL and PH
            PL_days.append(posteriorPDF_pL)
            PH_days.append(posteriorPDF_pH)
        #We've found the probability of being "both on" or "one off" for each day.
        #Add the arrays of these to our classes' collection of PLs and PHs
        self.PL_distributions.append(PL_days[1:len(PL_days)])
        self.PH_distributions.append(PH_days[1:len(PH_days)])
        return

    def _poisson(self,mu,x):
        #TODO: If x > 100, default to a Gaussian
        return np.exp(-mu)*(mu**(x))/scm.factorial(x)

#This class runs an sequential probability ratio test.  First, the 
#Null hypothesis is treated as the first 100 days of data's average.
#From there, SPRT is run assuming underlying poisson distributions for
#The null hypothesis and then a second case which is some fraction of
#The null hypothesis average.
class SPRTAnalysis(ExperimentalAnalysis):
    def __init__(self, CL_turnon=0.997, CL_turnoff=0.997, \
            initdays=365, numsigma=3.0):
        super(SPRTAnalysis, self).__init__()
        #In below, H = hypothesis
        self.aon = 1.0 - CL_turnon #Probability for falsely rejecting turn-on H
        self.aoff = 1.0 - CL_turnoff #Probability of falsely rejecting turn-off H
        self.numsigma = numsigma #Defines the rate for the other H
        self.initdays = initdays
        #Hold results from the most recently run experiment
        self.SPRTresultday = []
        self.SPRTresult = []
        self.SPRTaccbound = []
        self.SPRTrejbound = []
        #Hold results from many experiments
        self.SPRT_rejdays = []
        self.SPRT_accdays = []
        self.SPRT_unccount = 0

    def __call__(self, ExpGen):
        super(SPRTAnalysis, self).__call__(ExpGen)
        self.ExpCheck()
        self.RunSPRT()

    def ExpCheck(self):
        if len(self.Current_Experiment.coredict["known_cores"]) != 1:
            print("Experiment does not have one known core.  Should not"+\
                    "run this analysis.")

    def RunSPRT(self):
        '''
        This grabs all of the days where the known core was on.  We then
        calculate the null hypothesis average based on the value in
        self.initdays.  We then run an SPRT with the data binned into
        self.daysperbin days and see if we reject the null hypothesis.'''
        #reinitalize these results in preparation for SPRT results
        self.SPRTresultday = []
        self.SPRTtestpredict = []
        self.SPRTresult = []
        self.SPRTaccbound = []
        self.SPRTrejbound = []
        days_reacon = []
        events_ondays = []
        SPRT_daysbinned = []
        for j,n_on in enumerate(self.Current_Experiment.core_status_array):
            if n_on == 1:   #Day where known core is on
                days_reacon.append(self.Current_Experiment.experiment_days[j])
                events_ondays.append(self.Current_Experiment.events[j])
        events_ondays = np.array(events_ondays)
        plt.show()
        #Calculate the null hypothesis average
        testavg = float(np.sum(events_ondays[0:self.initdays]))/ \
                float(self.initdays)
        testavgunc = np.sqrt(float(np.sum(events_ondays[0:self.initdays])))/ \
                float(self.initdays)
        #Other hypothesis is that the average is half that of the nullavg
        turnoffthresh = testavg - (self.numsigma * testavgunc)
        turnonthresh = testavg + (self.numsigma * testavgunc)
        #Only run SPRT with days after first self.initdays amount
        SPRT_testdays = events_ondays[self.initdays:len(days_reacon)]
        #Bin the day events according to the input daysperbin
        determined = False
        for index in xrange(len(SPRT_testdays)):
            day = float(index + 1)
            test_stat = np.sum(SPRT_testdays[0:int(day)]) 
            #Gives the actual day in the experiment
            #self.SPRTresultday.append(days_reacon[self.initdays-1 + int(day)])
            self.SPRTtestpredict.append(testavg*day)
            self.SPRTresultday.append(days_reacon[self.initdays+int(day)-2])
            self.SPRTresult.append(test_stat)
            self.SPRTaccbound.append(self.U(day, turnonthresh,turnoffthresh,Uval=34.))
            self.SPRTrejbound.append(self.L(day, turnonthresh,turnoffthresh,Lval=-34.))
            if not determined:
                if test_stat < self.L(day,turnonthresh,turnoffthresh,Lval=-34.):
                    determined = True
                    self.SPRT_rejdays.append(days_reacon[self.initdays-1 + int(day)]) 
                if test_stat > self.U(day,turnonthresh,turnoffthresh,Uval=34.):
                    determined = True
                    self.SPRT_accdays.append(days_reacon[self.initdays-1 + int(day)])
        if not determined:
            self.SPRT_unccount+=1
        return

    def L(self,day, turnonthresh, turnoffthresh,Lval = None):
        #lower bound for SPRT; assumes poisson probabilities for null & other H
        if Lval is not None:
            return (Lval + (day *(turnonthresh - turnoffthresh))) / np.log(turnonthresh/turnoffthresh) 
        else:
            return (np.log(self.aon / (1.0 - self.aoff))+ (day *  \
                (turnonthresh - turnoffthresh))) / np.log(turnonthresh/turnoffthresh)  

    def U(self,day, turnonthresh,turnoffthresh,Uval = None):
        #lower bound for SPRT; assumes poisson probabilities for null & other H
        if Uval is not None:
            return (Uval + (day *(turnonthresh - turnoffthresh))) / np.log(turnonthresh/turnoffthresh) 
        else:
            return (np.log((1.0 - self.aon) / self.aoff)+ (day *  \
                (turnonthresh - turnoffthresh))) / np.log(turnonthresh/turnoffthresh)

#This analysis assumes one known core and some other unknown cores.
#A running average is performed in the "on" data to see when a difference
#is seen with >3sigma from the previous taken data.  If there is no 3sigma
#difference, it is absorbed into the data binned thus far.
class RunningAverageAnalysis(ExperimentalAnalysis):
    def __init__(self):
        super(RunningAverageAnalysis, self).__init__()
        self.par2_offbinfits = []
        self.mu_offbinfits = []
        self.csndf_offbinfits = []
        self.num_failfits = 0

    def __call__(self, ExpGen):
        super(RunningAverageAnalysis, self).__call__(ExpGen)
        self.ExpCheck()
        self.TestBackground(8)

    def ExpCheck(self):
        if len(self.Current_Experiment.coredict["known_cores"]) != 1:
            print("Experiment does not have one known core.  Should not"+\
                    "run this analysis.")

    def RunAverageTest(self, daysperbin):
        '''
        This grabs all of the days where the known core was on.  We then
        bin the data according to the input daysperbin, and see if the
        binned value at each step is outside the average of the previously
        collected data.
        '''
        day_reacon = []
        event_ondays = []
        events_rebinned = []
        for j,n_on in enumerate(self.Current_Experiment.core_status_array):
            if n_on == 1:   #Day where known core is on
                day_reacon.append(self.Current_Experiment.experiment_days[j])
                events_ondays.append(self.Current_Experiment.events[j])
        #Now, bin the day events according to the input daysperbin
        numondays = len(events_ondays)
        sumindex = 0
        while sumindex < numondays:
            binleft = sumindex
            sumindex+=daysperbin
            events_rebinned.append(np.sum(events_offdays[binleft:sumindex]))
        #TODO: we need to go bin by bin and see when/if the current bin
        #rests outside of the current average to a total of 3sigma difference
        #May need to increase the number of days in a bin here...
        #OTHER OPTIONS: if this looks hopeless, investigate using the SPRT
        #Cause I'm supes worried we don't have the stats to ever do this
        current_average = 0.0
        current_avgunc = 0.0

#This analysis is tuned to experiments generated with one known core and
#one unknown core.  
class UnknownCoreAnalysis(ExperimentalAnalysis):
    def __init__(self):
        super(UnknownCoreAnalysis, self).__init__()
        self.par2_offbinfits = []
        self.mu_offbinfits = []
        self.csndf_offbinfits = []
        self.num_failfits = 0

    def __call__(self, ExpGen):
        super(UnknownCoreAnalysis, self).__call__(ExpGen)
        self.ExpCheck()
        self.TestBackground(8)

    def ExpCheck(self):
        if len(self.Current_Experiment.coredict["known_cores"]) != 1:
            print("Experiment does not have one known core.  Should not"+\
                    "run this analysis.")
        if len(self.Current_Experiment.coredict["unknown_cores"]) != 1:
            print("Experiment does not have one unknown core. Should not"+\
                    "run this analysis.")

    def TestBackground(self, daysperbin):
        '''
        This grabs all of the days where the known core was off. We test
        to see if the background shape is consistent with a poisson 
        distribution of average given by that of the data itself.
        '''
        day_reacoff = []
        events_offdays = []
        events_rebinned = []
        for j,n_on in enumerate(self.Current_Experiment.core_status_array):
            if n_on == 1:   #Day where known core is off
                day_reacoff.append(self.Current_Experiment.experiment_days[j])
                events_offdays.append(self.Current_Experiment.events[j])
        #Now, bin the day events according to the input daysperbin
        numoffdays = len(events_offdays)
        sumindex = 0
        while sumindex < numoffdays:
            binleft = sumindex
            sumindex+=daysperbin
            events_rebinned.append(np.sum(events_offdays[binleft:sumindex]))
        #Now, the maximum likelihood fit for the Poisson distribution's
        #parameter is just the mean.

        import ROOT
        values = ROOT.TH1F("event_hist", "", np.max(events_rebinned) - \
                np.min(events_rebinned), np.min(events_rebinned), \
                np.max(events_rebinned))
        for entry in events_rebinned:
            values.Fill(entry)
        PoissonFit = ROOT.TF1('PoissonFit', self.fitfunction_poisson, \
                np.min(events_rebinned), np.max(events_rebinned), 2)
        PoissonFit.SetParameter(0, 1)
        PoissonFit.SetParameter(1, 1)
        #PoissonFit.SetParameter(2, 1)
        PoissonFit.SetParNames('par0', 'par1')#, 'par2')
        PoissonFit.SetLineColor(4)
        PoissonFit.SetLineWidth(2)
        PoissonFit.SetLineStyle(2)
        ROOT.gStyle.SetOptFit(0157)
#        ROOT.gPad.Modified()
        values.Fit('PoissonFit','Lq') #'q' for quiet
        #par2 = PoissonFit.GetParameter('par2')
        mu = PoissonFit.GetParameter('par1')
        chisq = PoissonFit.GetChisquare()
        ndf = PoissonFit.GetNDF()
        if chisq ==0 or ndf==0:
            self.num_failfits+=1
            return
        self.csndf_offbinfits.append(float(chisq) / float(ndf))
        self.mu_offbinfits.append(mu)
        #values.Draw()
        #PoissonFit.Draw('same')
        #time.sleep(50)

    def fitfunction_poisson(self, x, par):
        #if par[2] != 0:
           #if ROOT.TMath.Gamma((x[0]/par[2])+1) != 0:
            #    poisson = par[0] * ROOT.TMath.Power((par[1]/par[2]),(x[0]/par[2])) * (ROOT.TMath.Exp(-(par[1]/par[2])))/ROOT.TMath.Gamma((x[0]/par[2])+1)
        #else:
        #    poisson = 0
        import ROOT
        return par[0]*ROOT.TMath.Poisson(x[0], par[1])

class ScheduleAnalysis(ExperimentalAnalysis):
    def __init__(self):
        super(ScheduleAnalysis, self).__init__()
        self.num3siginarow = 14
        #Arrays that hold the event rate for each day where both
        #reactors are on or where at least one reactor is off
        self.onday_events = []
        self.offday_events = []
        #Array of ones and zeroes, each representing a day in the experiment
        #(0 no reactors on this day, 1 - one reactor on, etc.
        self.onoff_record = []

        #containers for results of CalcDailyAvgAndUnc
        self.onavg_cumul = []
        self.offavg_cumul = []
        self.onavg_cumul_unc = []
        self.offavg_cumul_unc = []
        self.tot_cumul_unc = []

        #Current experiments day where 3sigma is confirmed, and
        #Array of experiment determination day results
        self.currentexp_determination_day = 0
        self.determination_days = []
        self.num_nodetermine = 0

    def __call__(self, ExpGen):
        super(ScheduleAnalysis, self).__call__(ExpGen)
        self.OnOffGroup()
        self.CalcDailyAvgAndUnc()
        self.Get3SigmaDay()

    def OnOffGroup(self):
        '''
        Takes an experiment and groups together the days of data where
        both reactors were on, and groups days where at least one reactor was off.
        '''
        offday_events = []
        onday_events = []
        days_knownreacson = self.Current_Experiment.core_status_array
        for j,day in enumerate(self.Current_Experiment.experiment_days):
            if  days_knownreacson[j] == self.Current_Experiment.numknowncores:
                onday_events.append(self.Current_Experiment.events[j])
            else:
                offday_events.append(self.Current_Experiment.events[j])
        offday_events = np.array(offday_events)
        onday_events = np.array(onday_events)
        self.onday_events = onday_events
        self.offday_events = offday_events
        self.onoff_record = days_knownreacson

    def CalcDailyAvgAndUnc(self):
        '''
        Goes day-by-day and gets the average of IBD candidates and it's uncertainty 
        for 'all cores on' data and 'at least one core off' data based on all data that has
        been measured up to the current day.  Does this for every day in the experiment.
        '''
        offavg_cumul = []
        offavg_cumul_unc = []
        onavg_cumul = []
        onavg_cumul_unc = []
        experiment_day = 0
        #status codes: 0 - no cores on, 1 - one core on, etc.
        for j,status in enumerate(self.onoff_record):
            if status != self.Current_Experiment.numknowncores:
                #Get all previous data from 'cores off' days
                currentsum,daysofdata = self.GetDataToCurrentDay((j+1),'off')
                thisdays_offavg = (float(currentsum)/float(daysofdata))
                offavg_cumul.append(thisdays_offavg)
                #The uncertainty is the measured average divided by sqrt # days of
                #data
                offavg_cumul_unc.append(np.sqrt(float(thisdays_offavg))/np.sqrt(daysofdata))
                #Didn't get new on-day data; carry over the last day's statistics
                if j == 0:
                    onavg_cumul.append(0)
                    onavg_cumul_unc.append(0)
                else:
                    onavg_cumul.append(onavg_cumul[j-1])
                    onavg_cumul_unc.append(onavg_cumul_unc[j-1])

            if status == self.Current_Experiment.numknowncores:
                #Get all previous data from 'cores on' days
                currentsum,daysofdata = self.GetDataToCurrentDay((j+1),'on')
                thisdays_onavg = (float(currentsum)/float(daysofdata))
                onavg_cumul.append(thisdays_onavg)
                #The uncertainty is the measured average divided by sqrt # days of
                #data
                onavg_cumul_unc.append(np.sqrt(float(thisdays_onavg))/np.sqrt(daysofdata))
                #Didn't get new off-day data; carry over the last day's statistics
                if j == 0:
                    offavg_cumul.append(0)
                    offavg_cumul_unc.append(0)
                else:
                    offavg_cumul.append(offavg_cumul[j-1])
                    offavg_cumul_unc.append(offavg_cumul_unc[j-1])
        #analysis complete; place values in class containers
        self.onavg_cumul = onavg_cumul
        self.onavg_cumul_unc = onavg_cumul_unc
        self.offavg_cumul = offavg_cumul
        self.offavg_cumul_unc = offavg_cumul_unc

    def GetDataToCurrentDay(self, day, status):
        '''
        For the given status ('all on' or 'at least one off'), get all days of data
        in the vent BEFORE the given day summed together. returns the number of
        events and the number of days summed.
        '''
        events_tosum = []
        if status == 'on':
            for j,state in enumerate(self.onoff_record):
                if j == day:  #we've gotten our days.  break.
                    break
                if state == self.Current_Experiment.numknowncores:
                    events_tosum.append(self.Current_Experiment.events[j])
        elif status == 'off':
            for j,state in enumerate(self.onoff_record):
                if j == day:
                    break
                if state < self.Current_Experiment.numknowncores:
                    events_tosum.append(self.Current_Experiment.events[j])
        summed_events = np.sum(events_tosum)
        days_summed = len(events_tosum)
        return summed_events, days_summed

    def Get3SigmaDay(self):
        '''
        uses the onavg_cumul and offavg_cumul arrays filled with self.GetDataFromPastDays
        to determine what day in the experiment a 3sigma difference is achieved.
        Sets the current determination day and appends value to determination_days.
        '''
        daysofrunning = self.Current_Experiment.experiment_days
        dcount = 0
        dfound = False
        for j,day in enumerate(daysofrunning):
            day_onoffdiff = abs(self.onavg_cumul[j] - self.offavg_cumul[j])
            #Check if the data values are 3sigma apart
            day_sigma = abs(np.sqrt((self.onavg_cumul_unc[j])**2 + \
                    (self.offavg_cumul_unc[j])**2))
            if ((self.onavg_cumul_unc[j] == 0) or (self.offavg_cumul_unc[j] == 0)):
                #no data measured yet on this day for either on or off data
                self.tot_cumul_unc.append(0)
                continue
            self.tot_cumul_unc.append(day_sigma)
            if not dfound:
                if (day_onoffdiff <= (3 * day_sigma)):
                    dcount = 0
                    continue
                if (day_onoffdiff > (3 * day_sigma)):
                    dcount += 1
                    if dcount == self.num3siginarow:
                        self.currentexp_determination_day = day
                        self.determination_days.append(day)
                        dfound = True
                        continue
        #If still not determined, print that we need more data for a
        #Determination in this experiment
        if not dfound:
            print("No determination of on/off after length of experiment." + \
                    "Would have to run longer than {} days".format(self.Current_Experiment.totaldays))
            self.num_nodetermine+=1

