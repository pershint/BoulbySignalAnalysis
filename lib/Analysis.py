import numpy as np

#Class takes in a generated experiment (ExperimentGenerator class) and performs
#Some Analysis assuming we know exactly the days each core is on or off
class ExperimentalAnalysis(object):
    def __init__(self, sitename):
        self.sitename = sitename
        #Holds metadata of current experiment in analysis
        self.Current_Experiment = None
        #Arrays that hold the event rate for each day where both
        #reactors are on or where one reactor is off
        self.onday_events = []
        self.offday_events = []

        #Array of ones and zeroes, each representing a day in the experiment
        #(0 no reactors on this day, 1 - one reactor on, etc.
        self.onoff_record = []

    def __call__(self, ExpGen):
        self.Current_Experiment = ExpGen

    def OnOffGroup(self):
        '''
        Takes an experiment and groups together the days of data where
        both reactors were on, and groups days where at least one reactor was off.
        '''
        offday_events = []
        onday_events = []
        days_bothreacson = self.Current_Experiment.core_status_array
        for j,day in enumerate(self.Current_Experiment.experiment_days):
            if  days_bothreacson[j] == self.Current_Experiment.numcores:
                onday_events.append(self.Current_Experiment.events[j])
            else:
                offday_events.append(self.Current_Experiment.events[j])
        offday_events = np.array(offday_events)
        onday_events = np.array(onday_events)
        self.onday_events = onday_events
        self.offday_events = offday_events
        self.onoff_record = days_bothreacson

class Analysis2(ExperimentalAnalysis):
    def __init__(self, sitename):
        super(Analysis2, self).__init__(sitename)

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
        super(Analysis2, self).__call__(ExpGen)
        self.OnOffGroup()
        self.CalcDailyAvgAndUnc()
        self.Get3SigmaDay()

    def CalcDailyAvgAndUnc(self):
        '''
        Goes day-by-day and gets the average of IBD candidates and it's uncertainty 
        for 'both cores on' data and 'one core off' data based on all data that has
        been measured up to the current day.  Does this for every day in the experiment.
        '''
        offavg_cumul = []
        offavg_cumul_unc = []
        onavg_cumul = []
        onavg_cumul_unc = []
        experiment_day = 0
        #status codes: 0 - no cores on, 1 - one core on, etc.
        for j,status in enumerate(self.onoff_record):
            if status != self.Current_Experiment.numcores:
                #Get all previous data from 'cores off' days
                currentsum,daysofdata = self.GetDataToCurrentDay((j+1),'off')
                thisdays_offavg = (float(currentsum)/float(daysofdata))
                offavg_cumul.append(thisdays_offavg)
                #The uncertainty is the measured average divided by sqrt # days of
                #data
                offavg_cumul_unc.append(float(thisdays_offavg)/np.sqrt(daysofdata))
                #Didn't get new on-day data; carry over the last day's statistics
                if j == 0:
                    onavg_cumul.append(0)
                    onavg_cumul_unc.append(0)
                else:
                    onavg_cumul.append(onavg_cumul[j-1])
                    onavg_cumul_unc.append(onavg_cumul_unc[j-1])

            if status == self.Current_Experiment.numcores:
                #Get all previous data from 'cores on' days
                currentsum,daysofdata = self.GetDataToCurrentDay((j+1),'on')
                thisdays_onavg = (float(currentsum)/float(daysofdata))
                onavg_cumul.append(thisdays_onavg)
                #The uncertainty is the measured average divided by sqrt # days of
                #data
                onavg_cumul_unc.append(float(thisdays_onavg)/np.sqrt(daysofdata))
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
                if state == self.Current_Experiment.numcores:
                    events_tosum.append(self.Current_Experiment.events[j])
        elif status == 'off':
            for j,state in enumerate(self.onoff_record):
                if j == day:
                    break
                if state < self.Current_Experiment.numcores:
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

class ExperimentAnalysis1(object):
    def __init__(self, binning_choices,doReBin):
        #Bool for if reBinning analysis should be performed
        self.doReBin = doReBin
        
        #Holds metadata of current experiment in analysis
        self.Current_Experiment = 'no current experiment'

        #Arrays that hold the event rate for each day where both
        #reactors are on or where one reactor is off
        self.onday_events = []
        self.offday_events = []

        #Array of ones and zeroes, each representing a day in the experiment
        #(1 - both reactors were on on this day, 0 - a reactor was off)
        self.onoff_record = []

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
        self.currentexp_determination_day = 0

        #Array is filled with determination days by running self.OnOffStats
        self.determination_days = []
        self.determ_day_inexp = []

    def __call__(self, ExpGen):
        self.Current_Experiment = ExpGen

        self.OnOffGroup(self.Current_Experiment)
        AvgLargerSetEvents = True
        self.OnOffStats(AvgLargerSetEvents)
        if self.doReBin:
            for bin_choice in self.binning_choices:
                self.ReBinningStudy(bin_choice)

    def OnOffStats(self,AvgLargerSetEvents):
        '''
        Compares data from days when reactors were both on and when one reactor
        was off.  Determines how many days of data for each are needed to get a
        3sigma difference between the values.
        '''
        data = {'ondata':self.onday_events, 'offdata':self.offday_events}
        smallerdata = 'unknown'
        smallerdatalen = np.min([len(data['ondata']),len(data['offdata'])])
        largerdatalen = np.max([len(data['ondata']),len(data['offdata'])])
        #if true, the following takes the larger data set, rebins the larger set
        #to be the length of the smaller set but with the value as the average
        #Events per day for that rebinned data.  Essentially, lets you utilize
        #The larger data set to it's fullest when comparing to smaller set.
        if AvgLargerSetEvents:
            bin_choice = int(float(largerdatalen) / float(smallerdatalen))
            rebinned_ondata, rebinned_offdata, lost_days = self.ReBin_Days(data['ondata'], \
                    data['offdata'], bin_choice)
            if (int(len(data['ondata'])) > int(len(data['offdata']))):
                smallerdata = 'offdata'
                data['ondata'] = (rebinned_ondata / float(bin_choice))
            elif (int(len(data['offdata'])) > int(len(data['ondata']))):
                smallerdata = 'ondata'
                data['offdata'] = rebinned_offdata / float(bin_choice)

        daysofrunning = np.arange(1,(smallerdatalen+1),1)
        self.csum_numdays = daysofrunning
        determined = False
        dcount = 0
        for day in daysofrunning:
            totalondata = np.sum(data['ondata'][0:day])
            totaloffdata = np.sum(data['offdata'][0:day])
            onoffdiff = abs(totalondata - totaloffdata)
            self.csum_on.append(totalondata)
            self.csum_off.append(totaloffdata)
            #Check if the data values are 3sigma apart
            ontoterr = np.sqrt(totalondata)
            offtoterr = np.sqrt(totaloffdata)
            avg_sigma = abs(np.sqrt((ontoterr)**2 + (offtoterr)**2))
            if not determined:
                if (onoffdiff <= (3 * avg_sigma)):
                    dcount = 0
                if (onoffdiff > (3 * avg_sigma)):
                    dcount += 1
                if dcount == 14:
                    self.currentexp_determination_day = day
                    self.determination_days.append(day)
                    experiment_determ_day = self.Dday_To_Eday(day,smallerdata)
                    self.determ_day_inexp.append(experiment_determ_day)
                    determined = True
        #If still not determined, print that we need more data for a
        #Determination in this experiment
        print("No determination of on/off after length of experiment." + \
                "Would have to run longer than current experiment length.")

    def Dday_To_Eday(self,day,smallerdata):
        '''
        Takes in # days of data needed for determination and converts to
        A day in the experiment.  Whichever is the smaller data set is
        the set that limits how fast we get our result.
        '''
        experiment_day = 0
        determ_counter = 0
        if smallerdata == 'offdata':
            for reactor_state in self.onoff_record:
                experiment_day += 1
                if reactor_state == 0:
                    #This is a day from the smaller data set; contributes to
                    #determination day
                    determ_counter += 1
                if determ_counter == day:
                    #Reached our successful determination day in experiment!
                    return experiment_day

        if smallerdata == 'ondata':
            for reactor_state in self.onoff_record:
                experiment_day += 1
                if reactor_state == 1:
                    #This is a day from the smaller data set; contributes to
                    #determination day
                    determ_counter += 1
                if determ_counter == day:
                    #Reached our successful determination day in experiment!
                    return experiment_day

    def OnOffGroup(self, ExpGen):
        '''
        Takes an experiment and groups together the days of data where
        both reactors were on, and groups days where reactor was off.
        Can only be called if ExpGen.resolution = 1.
        '''
        offday_events = []
        onday_events = []
        days_bothreacson = ExpGen.core_status_array
        for j,day in enumerate(ExpGen.experiment_days):
            if  days_bothreacson[j] == 1:
                onday_events.append(ExpGen.events[j])
            else:
                offday_events.append(ExpGen.events[j])
        offday_events = np.array(offday_events)
        onday_events = np.array(onday_events)
        self.onday_events = onday_events
        self.offday_events = offday_events
        self.onoff_record = days_bothreacson

    def ReBinningStudy(self,bin_choice):
        #if 1 < bin_choice < self.Current_Experiment.totaldays, rebin events
        if 1 < bin_choice < self.Current_Experiment.totaldays:
            rebinned_ondays, rebinned_offdays, lost_days = \
                    self.ReBin_Days(self.onday_events, self.offday_events, bin_choice)
        #Now, calculate the average and standard deviation of each
        self.binned_onday_avg.append(np.average(rebinned_ondays))
        self.binned_onday_stdev.append(np.std(rebinned_ondays))
        self.binned_offday_avg.append(np.average(rebinned_offdays))
        self.binned_offday_stdev.append(np.std(rebinned_offdays))

        onda = (np.average(rebinned_ondays))
        ondstd = (np.std(rebinned_ondays))
        offda = (np.average(rebinned_offdays))
        offdstd = (np.std(rebinned_offdays))
        
        if DEBUG:
            print("EXPIERMENT RAN FOR {} DAYS".format(self.Current_Experiment.totaldays))
            print("DAYS BOTH ON, DAYS ONE REAC OFF: {0},{1}".format(len(self.onday_events),len(self.offday_events)))
            print("BINNING OF ON/OFF DAY DATA: {0}".format(bin_choice))
            print("ON DAY AVERAGE/STDEV: {0} / {1}".format(onda, ondstd))
            print("OFF DAY AVERAGE/STDEV: {0} / {1}".format(offda, offdstd))
            print("# DAYS LOST IN REBINNING [ONDAYS, OFFDAYS]: {0}".format(lost_days))

    def ReBin_Days(self, onday_events, offday_events, bin_choice):
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

        event_data = {'ondays':onday_events, 'offdays':offday_events}
        for datatype in event_data:
            step = 1
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

