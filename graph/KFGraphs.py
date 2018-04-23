import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#Graphs that plot results from the Kalman Filter Analysis

def Rebin_PLPH(PL_dist, PH_dist, daysperbin=3):
    '''Re-bins the probability distributions and averages the days in each bin'''
    PL_rebinned = []
    PH_rebinned = []
    this_day = 0
    for day in xrange(len(PH_dist)/daysperbin):
        if day + daysperbin > len(PH_dist):
            break
        else:
            PH_rebinned.append(np.sum(PH_dist[this_day:this_day+daysperbin])/float(daysperbin))
            PL_rebinned.append(np.sum(PL_dist[this_day:this_day+daysperbin])/float(daysperbin))
        this_day+=daysperbin
    PH_rebinned = np.array(PH_rebinned)
    PL_rebinned = np.array(PL_rebinned)
    return PL_rebinned, PH_rebinned

def PLPH_Plotter(KalmanAnalysisDict,daysperbin=3):
    '''Plots the first PL and PH distribution in the analysis results dictionary'''
    PH_dist = np.array(KalmanAnalysisDict["PH_distributions"][0])
    PL_dist = np.array(KalmanAnalysisDict["PL_distributions"][0])
    Exp_days = np.arange(0,KalmanAnalysisDict["schedule_dict"]["TOTAL_RUN"],daysperbin)
    Exp_days = Exp_days[1:len(Exp_days)]
    sns.set_style("whitegrid")
    sns.axes_style("whitegrid")
    xkcd_colors = ['slate blue', 'light eggplant', 'warm pink', 'green', 'grass']
    sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #First, we rebin the PL and PH distributions
    PL_rebinned,PH_rebinned = Rebin_PLPH(PL_dist, PH_dist,daysperbin=daysperbin)
    #Plot the PL days
    ax.plot(Exp_days,PH_rebinned, alpha=0.8,linewidth=4,label="P_high")
    ax.plot(Exp_days,PL_rebinned, alpha=0.8,linewidth=4,label="P_low")
    plt.legend(loc=1)
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
    PL_rebinned,PH_rebinned = Rebin_PLPH(PL_dist, PH_dist,daysperbin=daysperbin)
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
    plt.title("State of cores as predicted by Kalman Filter (%f CL) \n"%(round(CLpc,1)+\
            "(1=both on, 0=one off, 1/2=indeterminant)",fontsize=36)
    plt.xlabel("Experiment day",fontsize=34)
    plt.ylabel("Predicted reactor state",fontsize=34)
    plt.show()
