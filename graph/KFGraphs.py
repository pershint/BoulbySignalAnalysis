import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#Graphs that plot results from the Kalman Filter Analysis

def _AddOpMap(ScheduleDict,ax):
    '''Adds the operational map for the input experiment to the current plot'''
    #TODO: ADD THE DAYS WHERE A SHUTDOWN HAPPENS TO THE OP MAP
    schedule=ScheduleDict
    print(schedule)
    kshutoff_starts = np.empty(0)
    kshutoff_ends = np.empty(0)
    kmaint_starts = np.empty(0) 
    kmaint_ends = np.empty(0)
    killdays = np.empty(0)
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
    for j,core in enumerate(schedule["KILL_CORES"]):
        if core in schedule["CORETYPES"]["known_cores"]:
            killdays = np.append(killdays,schedule["KILL_DAYS"][j])

    print(killdays)
    if kshutoff_starts is not None:
        havesoffbox = False
        for j,val in enumerate(kshutoff_starts):
            if not havesoffbox:
                ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                    alpha=0.25, label="one off, shutdown\n truth")
                havesoffbox = True
            else:
                ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                    alpha=0.25)
    if kmaint_starts is not None and (int(schedule["MAINTENANCE_TIME"])>0):
        havemoffbox = False
        for j,val in enumerate(kmaint_starts):
            if not havemoffbox:
                ax.axvspan(kmaint_starts[j],kmaint_ends[j], 
                        color='orange', 
                    alpha=0.3, label="one off, maintenance\n truth")
                havemoffbox = True
            else:
                ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                    alpha=0.3)
    if killdays is not None:
        havekillbox = False
        for j,val in enumerate(killdays):
            if not havekillbox:
                ax.axvspan(killdays[j],schedule["TOTAL_RUN"], color='red', 
                    alpha=0.3, label="Permanent shutdown\n truth")
                ax.vlines(x=killdays[j],ymin=-3, ymax=3,  
                color="red",
                linewidth=4,alpha=0.4)
                havemoffbox = True
            else:
                ax.axvspan(killdays[j],schedule["TOTAL_RUN"], color='red', 
                    alpha=0.3)
                ax.vlines(x=killdays[j], ymin=0, ymax=1, 
                color="red",linewidth=4,alpha=0.4)
    return ax

def Rebin_Pdists(Prob_array, Exp_days, daysperbin=3):
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

def PH_Plotter(ForwardBackAnalysisDict,daysperbin=3,use_opmap=True,mark="line"):
    '''Plots the first PH distribution in the analysis results dictionary'''
    PH_dist = np.array(ForwardBackAnalysisDict["PH_dist_train"][3])
    Exp_days = np.arange(1,ForwardBackAnalysisDict["schedule_dict_train"]["TOTAL_RUN"]+1,daysperbin)
    #First, we rebin the PL and PH distributions
    probarr,Exp_days = Rebin_Pdists([PH_dist],Exp_days, daysperbin=daysperbin)
    [PH_rebinned] = probarr
    print("LEN EXP DAYS: " + str(len(Exp_days)))
    print("LEN PH_DIST: " + str(len(PH_rebinned)))
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['light eggplant', 'black', 'slate blue', 'warm pink', 'green', 'grass']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    if mark=="line":
        ax.plot(Exp_days,PH_rebinned, alpha=0.8,linewidth=4,label="P(both cores on)")
    elif mark=="point":
        ax.plot(Exp_days,PH_rebinned, alpha=0.8,linestyle="none",marker="o",
                markersize=5)
    if use_opmap is True:
        ax = _AddOpMap(ForwardBackAnalysisDict["schedule_dict_train"],ax)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title("Probability of reactor states at Hartlepool per day\n"+\
            "as predicted by Forward-Backward Algorithm",fontsize=32)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in WATCHMAN observation",fontsize=30)
    plt.ylabel("Probability that both \n Hartlepool cores are on",fontsize=30)
    #plt.legend(loc=5)
    plt.show()

def _ErrBars_PH_Spread_FC(PH_dist, PH_average, CL):
    PH_90hi = []
    PH_90lo = []
    binedges = np.arange(0.0,1.0 + (0.9/60), (1.0/60.0))
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


def PH_Spread(ForwardBackAnalysisDict,daysperbin=1,use_opmap=True):
    '''Plots the average and 90% CL bands (with overcoverage) of PH distributions 
    found during training in the given results dictionary'''
    CL = ForwardBackAnalysisDict["band_CL"]
    PH_dist = np.array(ForwardBackAnalysisDict["PH_dist_train"])
    PH_90hi, PH_90lo = ForwardBackAnalysisDict['PH_CLhi'], ForwardBackAnalysisDict["PH_CLlo"]
    numexpts = len(PH_dist)
    PH_median = np.average(PH_dist, axis=0)
    Exp_days = np.arange(1,ForwardBackAnalysisDict["schedule_dict_train"]["TOTAL_RUN"]+1,daysperbin)
    #First, we rebin the PL and PH distributions
    parr,Exp_days = Rebin_Pdists([PH_median,PH_90hi, PH_90lo],
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
       ax = _AddOpMap(ForwardBackAnalysisDict["schedule_dict_train"],ax)
    ax.vlines(Exp_days, PH_90loreb, PH_90hireb, color='g',alpha=0.8)
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

def Show_CLBands(ForwardBackAnalysisDict,optoshow="all"):
    '''Plots the regions that the "both cores on" and "one core off" should lie
    within to the given CL, according to the training data'''
    Exp_days = np.arange(0,ForwardBackAnalysisDict["schedule_dict_train"]["TOTAL_RUN"],1)
    numexpts = len(ForwardBackAnalysisDict["PH_dist_train"])
    if ForwardBackAnalysisDict["band_CL"] is None:
        print("You must train this result's CL bands to plot them.")
        return
    CL = ForwardBackAnalysisDict["band_CL"]
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['green','green', 'red', 'red']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    CL = str(np.round(CL,2))
    plt.title("Bands of Hartlepool operational state to %s CL\n"%(CL) + \
            "Determined using %i statistical experiments"%(numexpts),fontsize=32)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in experiment",fontsize=30)
    plt.ylabel("Probablity region covered by FB algorithm",fontsize=30)
    colorstopick = ['b','g','orange','red','purple']
    banddict = ForwardBackAnalysisDict["banddict"]
    if banddict is None:
        print("You must train your CL bands to make this plot.")
        return
    print("BANDDICT: " + str(banddict))
    for j,band in enumerate(banddict):
        bandtoshow=None
        if band==optoshow:
            bandtoshow=band
        elif band=="all":
            bandtoshow=band
        else:
            continue
        ax.hlines(y=banddict[bandtoshow][1], xmin=Exp_days[0], xmax=Exp_days[len(Exp_days)-1], 
                color=colorstopick[j],
                label=band,linewidth=5,alpha=0.6)
        ax.hlines(banddict[bandtoshow][0], Exp_days[0], Exp_days[len(Exp_days)-1], color=colorstopick[j],
                linewidth=5,alpha=0.8)
        ax.fill_between(Exp_days, banddict[bandtoshow][0], banddict[bandtoshow][1], 
                color=colorstopick[j], alpha=0.2)
    box = ax.get_position()
    ax.set_ylim([0,1])
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=16)
    plt.show()

def PlotTestPrediction(ForwardBackAnalysisDict,exptno=0,use_opmap=True,optoshow="all"):
    '''Plots the trained CL bands and the first test data's probability distribution.
    Only takes results from the Forward-Backward Algorithm as input'''
    Exp_days = np.arange(0,ForwardBackAnalysisDict["schedule_dict_train"]["TOTAL_RUN"],1)
    numexpts = len(ForwardBackAnalysisDict["PH_dist_train"])
    PH_dist = np.array(ForwardBackAnalysisDict["PH_dist_test"][0])
    OpCurves = ForwardBackAnalysisDict["Op_predictions"][0]
    CL = ForwardBackAnalysisDict["band_CL"]
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['purple','red', 'black']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    for optype in OpCurves:
        if optoshow=="all":
            ax.plot(Exp_days, OpCurves[optype], alpha=0.8,linewidth=5,label=optype + "\nprediction")
        elif optoshow == optype:
            ax.plot(Exp_days, OpCurves[optype], alpha=0.8,linewidth=5,label=optype + "\nprediction")
    if use_opmap is True:
        ax = _AddOpMap(ForwardBackAnalysisDict["schedule_dict_test"],ax)
    plt.title("Judge's prediction of Hartlepool state\n"+\
            "(trained using %i training experiments)"%(numexpts),fontsize=30)
    plt.tick_params(labelsize=26)
    plt.xlabel("Day in WATCHMAN observation",fontsize=30)
    plt.ylabel("Judge's prediction of state \n(1=yes, 0=no)",fontsize=30)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=18)
    plt.show()

def PH_OpRegionsWithFirstTest(ForwardBackAnalysisDict,optoshow="all",showatimewindow=False):
    '''Plots the trained CL bands and the first test data's probability distribution.
    Only takes results from the Forward-Backward Algorithm as input'''
    Exp_days = np.arange(0,ForwardBackAnalysisDict["schedule_dict_test"]["TOTAL_RUN"],1)
    numtrainexpts = len(ForwardBackAnalysisDict["PH_dist_train"])
    PH_dist = np.array(ForwardBackAnalysisDict["PH_dist_test"][2])
    CL = ForwardBackAnalysisDict["band_CL"]
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['cobalt','purple', 'red', 'red']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #Plot the PL days
    ax.plot(Exp_days,PH_dist, alpha=0.8,marker="o",linestyle="none",label="Test data, \n FB algorithm output")
    plt.title("Visualization of Judge's search for single core shutdowns "
            "(Judge's \n%s%% CL bands trained "%(str(np.round(CL,2)*100.0)) + \
            "using %i training experiments)"%(numtrainexpts),fontsize=28)
    plt.tick_params(labelsize=24)
    plt.xlabel("Day in experiment",fontsize=26)
    plt.ylabel("Probability both reactors are on",fontsize=26)
    colorstopick = ['g','b','orange','red','purple']
    banddict = ForwardBackAnalysisDict["banddict"]
    if banddict is None:
        print("You must train your CL bands to make this plot.")
        return
    print("BANDDICT: " + str(banddict))
    for j,band in enumerate(banddict):
        bandtoshow=None
        if band==optoshow:
            bandtoshow=band
        elif band=="all":
            bandtoshow=band
        else:
            continue
        ax.hlines(y=banddict[bandtoshow][1], xmin=Exp_days[0], xmax=Exp_days[len(Exp_days)-1], 
                color=colorstopick[j],
                label="One core shutdown\n interval from training",linewidth=5,alpha=0.6)
        ax.hlines(banddict[bandtoshow][0], Exp_days[0], Exp_days[len(Exp_days)-1], color=colorstopick[j],
                linewidth=5,alpha=0.8)
        ax.fill_between(Exp_days, banddict[bandtoshow][0], banddict[bandtoshow][1], 
                color=colorstopick[j], alpha=0.2)
    if showatimewindow:
        ax.vlines(x=100, ymin=0, ymax=1, 
                color="black",
                label="Time window interval\n from Hartlepool model",linewidth=5,alpha=0.8)
        ax.vlines(x=160,  ymin=0, ymax=1, color="black",
                linewidth=5,alpha=0.8)
        ax.fill_between(np.arange(100,160,1), 0, 1, 
                color="black", alpha=0.2)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=18)
    plt.show()


def OneCoreOff_CL(KalmanAnalysisDict,daysperbin=3,CL=0.683):
    '''Plots the first PL and PH distribution in the analysis results dictionary'''
    PH_dist = np.array(KalmanAnalysisDict["PH_dist_train"][3])
    Exp_days = np.arange(0,KalmanAnalysisDict["schedule_dict_train"]["TOTAL_RUN"],daysperbin)
    Exp_days = Exp_days[1:len(Exp_days)]
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['midnight']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #First, we rebin the PL and PH distributions
    [PL_rebinned,PH_rebinned], exp_days = Rebin_Pdists([PL_dist, PH_dist],daysperbin=daysperbin)
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
