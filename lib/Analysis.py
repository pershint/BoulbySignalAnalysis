import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as scs
import ROOT

#Class takes in a generated experiment (ExperimentGenerator class) and performs
#Some Analysis assuming we know exactly the days each core is on or off
class ExperimentalAnalysis(object):
    def __init__(self, sitename):
        self.sitename = sitename
        #Holds metadata of current experiment in analysis
        self.Current_Experiment = None

    def __call__(self, ExpGen):
        self.Current_Experiment = ExpGen

#This analysis is tuned to experiments generated with one known core and
#one unknown core.  
class UnknownCoreAnalysis(ExperimentalAnalysis):
    def __init__(self, sitename):
        super(UnknownCoreAnalysis, self).__init__(sitename)
        self.par2_offbinfits = []
        self.mu_offbinfits = []
        self.chisq_offbinfits = []
    def __call__(self, ExpGen):
        super(UnknownCoreAnalysis, self).__call__(ExpGen)
        self.ExpCheck()
        self.TestBackground(4)

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
            if n_on == 0:   #Day where known core is off
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
        values.Fit('PoissonFit','L') #'q' for quiet
        #par2 = PoissonFit.GetParameter('par2')
        mu = PoissonFit.GetParameter('par1')
        chisq = PoissonFit.GetChisquare()
        #self.par2_offbinfits.append(par2)
        self.chisq_offbinfits.append(chisq)
        self.mu_offbinfits.append(mu)
        values.Draw()
        PoissonFit.Draw('same')
        time.sleep(50)

    def fitfunction_poisson(self, x, par):
        #if par[2] != 0:
           #if ROOT.TMath.Gamma((x[0]/par[2])+1) != 0:
            #    poisson = par[0] * ROOT.TMath.Power((par[1]/par[2]),(x[0]/par[2])) * (ROOT.TMath.Exp(-(par[1]/par[2])))/ROOT.TMath.Gamma((x[0]/par[2])+1)
        #else:
        #    poisson = 0
        return par[0]*ROOT.TMath.Poisson(x[0], par[1])

class ScheduleAnalysis(ExperimentalAnalysis):
    def __init__(self, sitename):
        super(ScheduleAnalysis, self).__init__(sitename)

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
        d_days = 14  #Number of days in a row of 3sigma required for determination
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
                    if dcount == 14:
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

