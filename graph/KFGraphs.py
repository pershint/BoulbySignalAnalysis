import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#Graphs that plot results from the Kalman Filter Analysis

def Rebin_PLPHs(Prob_array, Exp_days, daysperbin=3):
    '''Re-bins the probability distributions and averages the days in each bin'''
    Probs_rebinned = []
    for j,parr in enumerate(Prob_array):
        this_day = 0
        parr_rebinned = []
        while ((this_day + daysperbin) < (len(parr))):#for day in xrange(len(Exp_days)):
            parr_rebinned.append(np.sum(parr[this_day:this_day+daysperbin])/float(daysperbin))
            this_day+=daysperbin
        P_rebinned = np.array(parr_rebinned)
        if len(Exp_days) > len(P_rebinned):
            Exp_days = list(Exp_days) 
            Exp_days.pop(len(Exp_days)-1)
        Probs_rebinned.append(P_rebinned)
    return Probs_rebinned, np.array(Exp_days)

def PLPH_Plotter(KalmanAnalysisDict,daysperbin=3,use_opmap=True):
    '''Plots the first PL and PH distribution in the analysis results dictionary'''
    PH_dist = np.array(KalmanAnalysisDict["PH_distributions"][0])
    PL_dist = np.array(KalmanAnalysisDict["PL_distributions"][0])
    Exp_days = np.arange(1,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1,daysperbin)
    #First, we rebin the PL and PH distributions
    probarr,Exp_days = Rebin_PLPHs([PL_dist, PH_dist],Exp_days, daysperbin=daysperbin)
    [PL_rebinned,PH_rebinned] = probarr
    print("LEN EXP DAYS: " + str(len(Exp_days)))
    print("LEN PH_DIST: " + str(len(PH_rebinned)))
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['light eggplant', 'black', 'slate blue', 'warm pink', 'green', 'grass']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    ax.plot(Exp_days,PH_rebinned, alpha=0.8,linewidth=4,label="P(both cores on)")
    if use_opmap is True:
        schedule=KalmanAnalysisDict['schedule_dict']
        kshutoff_starts = np.empty(0)
        kshutoff_ends = np.empty(0)
        kmaint_starts = np.empty(0) 
        kmaint_ends = np.empty(0)
        for core in schedule["SHUTDOWN_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kshutoff_starts = np.append(kshutoff_starts, \
                    schedule["SHUTDOWN_STARTDAYS"][core])
                kshutoff_ends = kshutoff_starts + schedule["OFF_TIME"]
        for core in schedule["MAINTENANCE_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kmaint_starts = np.append(kmaint_starts, \
                         schedule["MAINTENANCE_STARTDAYS"][core])
                kmaint_ends = kmaint_starts + schedule["MAINTENANCE_TIME"]

        if kshutoff_starts is not None:
            havesoffbox = False
            for j,val in enumerate(kshutoff_starts):
                if not havesoffbox:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2, label="Large Shutdown")
                    havesoffbox = True
                else:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2)
        if kmaint_starts is not None and (int(schedule["MAINTENANCE_TIME"])>0):
            havemoffbox = False
            for j,val in enumerate(kmaint_starts):
                if not havemoffbox:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4, label="Maintenance")
                    havemoffbox = True
                else:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4)
    #ax.plot(Exp_days,PL_rebinned, alpha=0.8,linewidth=4,label="P_low")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title("Probability of reactor states at Boulby per day\n"+\
            "as predicted by Forward-Backward Algorithm")
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in experiment",fontsize=30)
    plt.ylabel("Probability of state",fontsize=30)
    #plt.legend(loc=5)
    plt.show()

def PLPH_Spread(KalmanAnalysisDict,daysperbin=7,use_opmap=True):
    '''Plots the average and standard deviation of PL distribution for all
    simulated experiments in the given results dictionary'''
    PH_dist = np.array(KalmanAnalysisDict["PH_distributions"])
    PL_dist = np.array(KalmanAnalysisDict["PL_distributions"])
    numexpts = len(PH_dist)
    PH_average = np.average(PH_dist, axis=0)
    PH_stdev = np.std(PH_dist, axis=0)
    PL_average = np.average(PL_dist, axis=0)
    PL_stdev = np.std(PL_dist, axis=0)
    Exp_days = np.arange(1,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1,daysperbin)
    #First, we rebin the PL and PH distributions
    parr1,Exp_days = Rebin_PLPHs([PL_average, PH_average],Exp_days, daysperbin=daysperbin)
    parr2,Exp_days = Rebin_PLPHs([PL_stdev, PH_stdev],Exp_days, daysperbin=daysperbin)
    [PL_avgreb, PH_avgreb] = parr1
    [PL_stdreb, PH_stdreb] = parr2
    print("LEN EXP DAYS: " + str(len(Exp_days)))
    print("LEN PH_AVERAGEREBINNED: " + str(len(PH_avgreb)))
    print("LEN PH_STDEVREBINNED: " + str(len(PH_stdreb)))
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['green', 'black']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    ax.errorbar(x=Exp_days,y=PH_avgreb,yerr=PH_stdreb, alpha=0.8,
            linewidth=5,elinewidth=2,label="P(both cores on)")
    if use_opmap is True:
        schedule=KalmanAnalysisDict['schedule_dict']
        kshutoff_starts = np.empty(0)
        kshutoff_ends = np.empty(0)
        kmaint_starts = np.empty(0) 
        kmaint_ends = np.empty(0)
        for core in schedule["SHUTDOWN_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kshutoff_starts = np.append(kshutoff_starts, \
                    schedule["SHUTDOWN_STARTDAYS"][core])
                kshutoff_ends = kshutoff_starts + schedule["OFF_TIME"]
        for core in schedule["MAINTENANCE_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kmaint_starts = np.append(kmaint_starts, \
                         schedule["MAINTENANCE_STARTDAYS"][core])
                kmaint_ends = kmaint_starts + schedule["MAINTENANCE_TIME"]

        if kshutoff_starts is not None:
            havesoffbox = False
            for j,val in enumerate(kshutoff_starts):
                if not havesoffbox:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2, label="Large Shutdown")
                    havesoffbox = True
                else:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2)
        if kmaint_starts is not None and (int(schedule["MAINTENANCE_TIME"])>0):
            havemoffbox = False
            for j,val in enumerate(kmaint_starts):
                if not havemoffbox:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4, label="Maintenance")
                    havemoffbox = True
                else:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4)
    #ax.plot(Exp_days,PL_rebinned, alpha=0.8,linewidth=4,label="P_low")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title("Prediction spread of 'both cores on' probability in %i experiments\n"%(numexpts),
            fontsize=32)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in experiment",fontsize=30)
    plt.ylabel("Probability of state",fontsize=30)
    #plt.legend(loc=5)
    plt.show()

def _ErrBars_PLPH_Spread_FC(PH_dist, PH_average, CL):
    PH_90hi = []
    PH_90lo = []
    binedges = np.arange(0.0,1.0 + (0.9/30), (1.0/30.0))
    for i in xrange(len(PH_dist[0])): #Gets ith index of each day
        dayprobs = []
        for e in xrange(len(PH_dist)):
            dayprobs.append(PH_dist[e][i])
        dayprobs = np.array(dayprobs)
        hist, binedges = np.histogram(dayprobs,bins=binedges)
        #find the bin index where this average is located
        avgind = np.where(PH_average[i] < binedges)[0][0]
        #avgind is the index in hist that has the average value
        #Now, we move left and right, summing up the % of events we have.
        #Once we cross 90%CL, our bounds are defined by the edges of these
        #Bins.
        sumlength = np.max([avgind, len(hist)- avgind])
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
                current_CL += float(hist[avgind])/ tot_entries
            else:
                ##add the bin on ith side of prob. average
                #FIXME: Confirm you have overcoverage here
                if avgind-i >= 0:
                    current_CL += float(hist[avgind-i])/ tot_entries
                else:
                    summedalllo = True
                if avgind+i <= len(hist)-1:
                    current_CL += float(hist[avgind+i])/ tot_entries
                else:
                    summedallhi = True
            if current_CL >= CL:
                passed_CL = True
                break
        if summedallhi is True:
            PH_90hi.append(binedges[len(binedges)-1])
        else:
            PH_90hi.append(binedges[avgind+i])
        if summedalllo is True:
            PH_90lo.append(binedges[0])
        else:
            PH_90lo.append(binedges[avgind-i])
    return PH_90hi, PH_90lo

def PLPH_Spread_FC(KalmanAnalysisDict,daysperbin=7,use_opmap=True,CL=0.90):
    '''Plots the average and 90% CL bands (with overcoverage) of PH distribution for all
    simulated experiments in the given results dictionary'''
    PH_dist = np.array(KalmanAnalysisDict["PH_distributions"])
    numexpts = len(PH_dist)
    PH_average = np.average(PH_dist, axis=0)
    #Now, we need to calculate the 90% CL range for each day
    PH_90hi, PH_90lo = _ErrBars_PLPH_Spread_FC(PH_dist, PH_average, CL)
    Exp_days = np.arange(1,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1,daysperbin)
    #First, we rebin the PL and PH distributions
    parr,Exp_days = Rebin_PLPHs([PH_average,PH_90hi, PH_90lo],
            Exp_days, daysperbin=daysperbin)
    [PH_avgreb, PH_90hireb, PH_90loreb] = parr
    print("LEN EXP DAYS: " + str(len(Exp_days)))
    print("LEN PH_AVERAGEREBINNED: " + str(len(PH_avgreb)))
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['green','black', 'grass']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    asymm_error = np.array([PH_90loreb, PH_90hireb])
    print(asymm_error)
    ax.plot(Exp_days, PH_avgreb, alpha=0.8, linewidth=5,
            label="P(both cores on)")
    print(PH_90loreb)
    if use_opmap is True:
        schedule=KalmanAnalysisDict['schedule_dict']
        kshutoff_starts = np.empty(0)
        kshutoff_ends = np.empty(0)
        kmaint_starts = np.empty(0) 
        kmaint_ends = np.empty(0)
        for core in schedule["SHUTDOWN_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kshutoff_starts = np.append(kshutoff_starts, \
                    schedule["SHUTDOWN_STARTDAYS"][core])
                kshutoff_ends = kshutoff_starts + schedule["OFF_TIME"]
        for core in schedule["MAINTENANCE_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kmaint_starts = np.append(kmaint_starts, \
                         schedule["MAINTENANCE_STARTDAYS"][core])
                kmaint_ends = kmaint_starts + schedule["MAINTENANCE_TIME"]

        if kshutoff_starts is not None:
            havesoffbox = False
            for j,val in enumerate(kshutoff_starts):
                if not havesoffbox:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2, label="Large Shutdown")
                    havesoffbox = True
                else:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2)
        if kmaint_starts is not None and (int(schedule["MAINTENANCE_TIME"])>0):
            havemoffbox = False
            for j,val in enumerate(kmaint_starts):
                if not havemoffbox:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4, label="Maintenance")
                    havemoffbox = True
                else:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4)
    ax.vlines(Exp_days, PH_90loreb, PH_90hireb, color='g',alpha=0.8)
    #ax.plot(Exp_days,PL_rebinned, alpha=0.8,linewidth=4,label="P_low")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    CL = np.round(CL,2)
    plt.title("Prediction spread of 'both cores on' probability in %i experiments to %s CL\n"%(numexpts,str(CL))
            ,fontsize=32)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in experiment",fontsize=30)
    plt.ylabel("Probability of state",fontsize=30)
    #plt.legend(loc=5)
    plt.show()


def PLPH_Spread_FC_new(KalmanAnalysisDict,daysperbin=7,use_opmap=True,CL=0.90):
    '''Plots the average and 90% CL bands (with overcoverage) of PH distribution for all
    simulated experiments in the given results dictionary'''
    PH_dist = np.array(KalmanAnalysisDict["PH_distributions"])
    PH_90hi, PH_90lo = KalmanAnalysisDict['PH_CLhi'], KalmanAnalysisDict["PH_CLlo"]
    numexpts = len(PH_dist)
    PH_average = np.average(PH_dist, axis=0)
    #Now, we need to calculate the 90% CL range for each day
    Exp_days = np.arange(1,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1,daysperbin)
    #First, we rebin the PL and PH distributions
    parr,Exp_days = Rebin_PLPHs([PH_average,PH_90hi, PH_90lo],
            Exp_days, daysperbin=daysperbin)
    [PH_avgreb, PH_90hireb, PH_90loreb] = parr
    print("LEN EXP DAYS: " + str(len(Exp_days)))
    print("LEN PH_AVERAGEREBINNED: " + str(len(PH_avgreb)))
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['green','black', 'grass']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    asymm_error = np.array([PH_90loreb, PH_90hireb])
    print(asymm_error)
    ax.plot(Exp_days, PH_avgreb, alpha=0.8, linewidth=5,
            label="P(both cores on)")
    print(PH_90loreb)
    if use_opmap is True:
        schedule=KalmanAnalysisDict['schedule_dict']
        kshutoff_starts = np.empty(0)
        kshutoff_ends = np.empty(0)
        kmaint_starts = np.empty(0) 
        kmaint_ends = np.empty(0)
        for core in schedule["SHUTDOWN_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kshutoff_starts = np.append(kshutoff_starts, \
                    schedule["SHUTDOWN_STARTDAYS"][core])
                kshutoff_ends = kshutoff_starts + schedule["OFF_TIME"]
        for core in schedule["MAINTENANCE_STARTDAYS"]:
            if core in schedule["CORETYPES"]["known_cores"]:
                kmaint_starts = np.append(kmaint_starts, \
                         schedule["MAINTENANCE_STARTDAYS"][core])
                kmaint_ends = kmaint_starts + schedule["MAINTENANCE_TIME"]

        if kshutoff_starts is not None:
            havesoffbox = False
            for j,val in enumerate(kshutoff_starts):
                if not havesoffbox:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2, label="Large Shutdown")
                    havesoffbox = True
                else:
                    ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                        alpha=0.2)
        if kmaint_starts is not None and (int(schedule["MAINTENANCE_TIME"])>0):
            havemoffbox = False
            for j,val in enumerate(kmaint_starts):
                if not havemoffbox:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4, label="Maintenance")
                    havemoffbox = True
                else:
                    ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                        alpha=0.4)
    ax.vlines(Exp_days, PH_90loreb, PH_90hireb, color='g',alpha=0.8)
    #ax.plot(Exp_days,PL_rebinned, alpha=0.8,linewidth=4,label="P_low")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    CL = np.round(CL,2)
    plt.title("Prediction spread of 'both cores on' probability in %i experiments to %s CL\n"%(numexpts,str(CL))
            ,fontsize=32)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in experiment",fontsize=30)
    plt.ylabel("Probability of state",fontsize=30)
    #plt.legend(loc=5)
    plt.show()

def _findOpRegions(opmap, PH_90hi, PH_90lo):
    '''Returns the high and low bands consistent with "both cores on" and
    "one core off" to the given CL'''
    bothon_CLhi, bothon_CLlo = [], []
    offs_CLhi, offs_CLlo = [], []
    offm_CLhi, offm_CLlo = [], []
    #First, we build bothon, oneoff_S, and
    #oneoff_M regions

    for j,state in enumerate(opmap):
        if state == 'on':
            bothon_CLhi.append(PH_90hi[j])
            bothon_CLlo.append(PH_90lo[j])
        elif state == 'off_s':
            offs_CLhi.append(PH_90hi[j])
            offs_CLlo.append(PH_90lo[j])
        elif state == 'off_m':
            offm_CLhi.append(PH_90hi[j])
            offm_CLlo.append(PH_90lo[j])
        else:
            print("Something went wrong with defining states in your op maps...")
            return
    bothon_hiavg = np.average(bothon_CLhi)
    bothon_loavg = np.average(bothon_CLlo)
    offs_hiavg = np.average(offs_CLhi)
    offs_loavg = np.average(offs_CLlo)
    offm_hiavg = np.average(offm_CLhi)
    offm_loavg = np.average(offm_CLlo)
    return bothon_hiavg, bothon_loavg, offs_hiavg, offs_loavg, offm_hiavg, offm_loavg

def PLPH_OpRegions(KalmanAnalysisDict,CL=0.90):
    '''Plots the regions that the "both cores on" and "one core off" should lie
    within to the given CL'''
    try:
        fulldays = np.arange(1,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1,1)
        opmap = ["on"] *KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"]
    except KeyError:
        print("No core map generated/saved in data dictionary. Cannot run this " +\
                "function.")
        return
    coreops = KalmanAnalysisDict['schedule_dict']['OFFTYPE_MAP']
    for core in coreops:
        for j,dayop in enumerate(coreops[core]):
            if dayop == "S":
                opmap[j] = "off_s" 
            elif dayop == "M":
                opmap[j] = "off_m" 
    print("OPMAP: " + str(opmap))
    PH_dist = np.array(KalmanAnalysisDict["PH_distributions"])
    numexpts = len(PH_dist)
    PH_avg = np.average(PH_dist, axis=0)
    #Now, we need to calculate the 90% CL range for each day
    PH_CLhi, PH_CLlo = _ErrBars_PLPH_Spread_FC(PH_dist, PH_avg, CL)
    Exp_days = np.arange(1,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1)
    bothon_CLhi, bothon_CLlo, offs_CLhi, offs_CLlo , offm_CLhi, offm_CLlo = \
            _findOpRegions(opmap, PH_CLhi, PH_CLlo)
    print("BOTHON_LO: " + str(bothon_CLlo))
    #First, we rebin the PL and PH distributions
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['green','green', 'red', 'red']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    plt.title("Bands of reactor complex operational state to %f CL\n"%(CL) + \
            "Determined using %i statistical experiments"%(numexpts))
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in experiment",fontsize=30)
    plt.ylabel("Probability both reactors are on",fontsize=30)
    ax.hlines(y=bothon_CLhi, xmin=Exp_days[0], xmax=Exp_days[len(Exp_days)-1], color='g',
            label='Both on',linewidth=5,alpha=0.8)
    ax.hlines(bothon_CLlo, Exp_days[0], Exp_days[len(Exp_days)-1], color='g',
            linewidth=5,alpha=0.8)
    ax.fill_between(Exp_days, bothon_CLlo, bothon_CLhi, color='g', alpha=0.2)
    ax.hlines(offs_CLhi, Exp_days[0], Exp_days[len(Exp_days)-1], color='b',
            label='One off, shutdown', linewidth=5, alpha=0.8)
    ax.hlines(offs_CLlo, Exp_days[0], Exp_days[len(Exp_days)-1], color='b',
            linewidth=5, alpha=0.8)
    ax.fill_between(Exp_days, offs_CLlo, offs_CLhi, color='b', alpha=0.2)
    ax.hlines(offm_CLhi, Exp_days[0], Exp_days[len(Exp_days)-1], color='orange',
            label='One off, maintenance', linewidth=5, alpha=0.8)
    ax.hlines(offm_CLlo, Exp_days[0], Exp_days[len(Exp_days)-1], color='orange',
            linewidth=5, alpha=0.8)
    ax.fill_between(Exp_days, offm_CLlo, offm_CLhi, color='orange', alpha=0.2)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()


def OneCoreOff_CL(KalmanAnalysisDict,daysperbin=3,CL=0.683):
    '''Plots the first PL and PH distribution in the analysis results dictionary'''
    PH_dist = np.array(KalmanAnalysisDict["PH_distributions"][0])
    PL_dist = np.array(KalmanAnalysisDict["PL_distributions"][0])
    Exp_days = np.arange(0,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"],daysperbin)
    Exp_days = Exp_days[1:len(Exp_days)]
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['midnight']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #First, we rebin the PL and PH distributions
    [PL_rebinned,PH_rebinned], exp_days = Rebin_PLPHs([PL_dist, PH_dist],daysperbin=daysperbin)
    #Now, check if PL is >0.683 for each day or if PH > 0.683
    StateProb = []
    for measurement in PL_rebinned:
        if measurement < (1- CL):
            StateProb.append(1)
        elif measurement > CL:
            StateProb.append(0)
        else:
            StateProb.append(0.5)
    StateProb = np.array(StateProb)
    ax.plot(Exp_days,StateProb, alpha=0.8,linewidth=4,label="")
    CLpc = CL*100
    plt.title("State of cores as predicted by Kalman Filter (%f CL) \n"%(CLpc)+\
            "(1=both on, 0=one off, 1/2=indeterminant)",fontsize=36)
    plt.xlabel("Experiment day",fontsize=34)
    plt.ylabel("Predicted reactor state",fontsize=34)
    plt.show()
