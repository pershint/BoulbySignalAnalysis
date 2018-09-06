#This file contains methods for making different plots of
#results of running the SlidingWindowAnalysis in main.py.
#Script best used as follows:
#  - open up ipython
#  - Load up the results data json using the json library
#  - Import these methods in ipython
#  - Use functions with the loaded json as input

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def _ErrBars_Spread_FC(Prob_dists, P_average, CL,numbins=100):
    '''Takes in an array of Sliding Window results and returns the confidence limit
    bands where you expect to find any single moving window analysis value on that
    day.'''

    P_CLhi = []
    P_CLlo = []
    maxavg = np.max(P_average)
    binedges = np.arange(0.0, 1.1*maxavg , (1.0/numbins))
    for i in xrange(len(Prob_dists[0])): #Gets ith index of each day
        dayprobs = []
        for e in xrange(len(Prob_dists)):
            dayprobs.append(Prob_dists[e][i])
        dayprobs = np.array(dayprobs)
        hist, binedges = np.histogram(dayprobs,bins=binedges)
        #find the bin index where this average is located
        avgind = np.where(P_average[i] < binedges)[0][0]
        #avgind is the index in hist that has the average value
        #Now, we move left and right, summing up the % of events we have.
        #Once we cross CL%CL, our bounds are defined by the edges of these
        #Bins.
        sumlength = np.max([avgind, len(hist)- avgind])
        current_CL = 0.0
        tot_entries = float(hist.sum())
        past_CL = False
        summedalllo = False
        summedallhi = False
        for k in xrange(sumlength):
            if past_CL is True:
                outind = k
                break
            if k==0:
                current_CL += float(hist[avgind])/ tot_entries
            else:
                ##add the bin on ith side of prob. average
                #FIXME: Confirm you have overcoverage here
                if avgind-k >= 0:
                    current_CL += float(hist[avgind-k])/ tot_entries
                else:
                    summedalllo = True
                if avgind+k <= len(hist)-1:
                    current_CL += float(hist[avgind+k])/ tot_entries
                else:
                    summedallhi = True
            if current_CL >= CL:
                passed_CL = True
                break
        if summedallhi is True:
            P_CLhi.append(binedges[len(binedges)-1])
        else:
            P_CLhi.append(binedges[avgind+k])
        if summedalllo is True:
            P_CLlo.append(binedges[0])
        else:
            P_CLlo.append(binedges[avgind-k])
    return P_CLhi, P_CLlo

def _findOpRegions(coremap, P_CLhi, P_CLlo):
    '''Returns the high and low bands consistent with "both cores on" and
    "one core off" to the given CL'''
    bothon_CLhi, bothon_CLlo = [], []
    oneoff_CLhi, oneoff_CLlo = [], []
    for j,state in enumerate(coremap):
        if state == 2:
            bothon_CLhi.append(P_CLhi[j])
            bothon_CLlo.append(P_CLlo[j])
        elif state == 1:
            oneoff_CLhi.append(P_CLhi[j])
            oneoff_CLlo.append(P_CLlo[j])
        else:
            print("Finding OP regions for more than the 'both cores on' and "+\
                    "'one core off' states is not supported currently.")
            return
    bothon_hiavg = np.average(bothon_CLhi)
    bothon_loavg = np.average(bothon_CLlo)
    oneoff_hiavg = np.average(oneoff_CLhi)
    oneoff_loavg = np.average(oneoff_CLlo)
    return bothon_hiavg, bothon_loavg, oneoff_hiavg, oneoff_loavg 

def Window_OpRegions(WindowAnalysisDict,CL=0.68):
    '''Plots the regions that the "both cores on" and "one core off" should lie
    within to the given CL'''
    try:
        fulldays = np.arange(1,WindowAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1,1)
        coremap = WindowAnalysisDict['known_numcoreson']
    except KeyError:
        print("No core map generated/saved in data dictionary. Cannot run this " +\
                "function.")
        return
    P_dist = np.array(WindowAnalysisDict["avg_distributions"])
    numexpts = len(P_dist)
    P_avg = np.average(P_dist, axis=0)
    #Now, we need to calculate the 90% CL range for each day
    P_CLhi, P_CLlo = _ErrBars_Spread_FC(P_dist, P_avg, CL)
    Exp_days = np.arange(1,WindowAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1)
    bothon_CLhi, bothon_CLlo, oneoff_CLhi, oneoff_CLlo = \
            _findOpRegions(coremap, P_CLhi, P_CLlo)
    print("BOTHON_LO: " + str(bothon_CLlo))
    #First, we rebin the PL and PH distributions
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['green','green', 'red', 'red']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    CL = np.round(CL,2)
    plt.title("Bands of reactor complex operational state to %s CL\n"%(str(CL)) + \
            "Determined using %i statistical experiments"%(numexpts),fontsize=32)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day at center of window",fontsize=30)
    plt.ylabel("Average event rate (events/day)",fontsize=30)
    ax.hlines(y=bothon_CLhi, xmin=Exp_days[0], xmax=Exp_days[len(Exp_days)-1], color='g',
            label='Both on',linewidth=5,alpha=0.8)
    ax.hlines(bothon_CLlo, Exp_days[0], Exp_days[len(Exp_days)-1], color='g',
            linewidth=5,alpha=0.8)
    ax.fill_between(Exp_days, bothon_CLlo, bothon_CLhi, color='g', alpha=0.2)
    ax.hlines(y=bothon_CLlo, xmin=Exp_days[0], xmax=Exp_days[len(Exp_days)-1], color='orange',
            label='Transition',linewidth=5,alpha=0.8)
    ax.hlines(oneoff_CLhi, Exp_days[0], Exp_days[len(Exp_days)-1], color='orange',
            linewidth=5,alpha=0.8)
    ax.fill_between(Exp_days, oneoff_CLhi, bothon_CLlo, color='orange', alpha=0.2)
    ax.hlines(oneoff_CLhi, Exp_days[0], Exp_days[len(Exp_days)-1], color='b',
            label='One off', linewidth=5, alpha=0.8)
    ax.hlines(oneoff_CLlo, Exp_days[0], Exp_days[len(Exp_days)-1], color='b',
            linewidth=5, alpha=0.8)
    ax.fill_between(Exp_days, oneoff_CLlo, oneoff_CLhi, color='b', alpha=0.2)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

def WindowSpread_FC(WindowAnalysisDict,use_coremap=True,CL=0.90):
    P_dist = np.array(WindowAnalysisDict["avg_distributions"])
    numexpts = len(P_dist)
    P_average = np.average(P_dist, axis=0)
    #Now, we need to calculate the 90% CL range for each day
    P_90hi, P_90lo = _ErrBars_Spread_FC(P_dist, P_average, CL)
    Exp_days = np.arange(1,WindowAnalysisDict["schedule_dict"]["TOTAL_RUN"]+1,1)
    #First, we rebin the PL and PH distributions
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['green','black', 'grass']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    asymm_error = np.array([P_90lo, P_90hi])
    print(asymm_error)
    ax.plot(Exp_days, P_average, alpha=0.8, linewidth=5,
            label="Average event rate")
    print(P_90lo)
    if use_coremap is True:
        schedule=WindowAnalysisDict['schedule_dict']
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
    
    ax.vlines(Exp_days, P_90lo, P_90hi, color='g',alpha=0.8)
    #ax.plot(Exp_days,PL_rebinned, alpha=0.8,linewidth=4,label="P_low")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    CL = np.round(CL,2)
    plt.title("Confidence limits on average window event rate (%i expts,%s CL)\n"%(numexpts,str(CL)),
            fontsize=32)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day at center of window",fontsize=30)
    plt.ylabel("Average window event rate (events/day)",fontsize=30)
    #plt.legend(loc=5)
    plt.show()
