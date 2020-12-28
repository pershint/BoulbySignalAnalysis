#Functions for graphing different properties of a generated experiment
import copy as cp
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import MapMaker as mm

sns.set_style("darkgrid")
xkcd_colors = ['light eggplant', 'black', 'slate blue', 'warm pink', 'green', 'grass']
sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))

def Plot_KnownReacOnOff(GeneratedExperiment):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
#    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.unknown_core_onoffdays,
#            color='k', alpha=0.8)
#    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.unknown_core_events, marker = 'o', linestyle='none', color='k')
    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.core_status_array,
            color='blue', alpha=0.7, linewidth=3) 
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(16)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(16)
    ax.set_xlabel("Days since start of WATCHMAN observation",fontsize=24)
    ax.set_title("Default model of Hartlepool reactor plant operation \n"+\
            "(Schedule based on Hartlepool's operational history)",fontsize=32)
    ax.set_ylabel("Number of reactor cores operating on day",fontsize=24)
    ax.set_ylim([0,3])
    ax.grid(True)
    plt.show()

def Plot_AllReacOnOff(GeneratedExperiment):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
#    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.unknown_core_onoffdays,
#            color='k', alpha=0.8)
#    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.unknown_core_events, marker = 'o', linestyle='none', color='k')
    ax.plot(GeneratedExperiment.experiment_days, \
            GeneratedExperiment.known_numcoreson + \
            GeneratedExperiment.unknown_numcoreson,
            color='g', alpha=0.8, linewidth = 3) 
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(16)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(16)
    ax.set_xlabel("days", fontsize = 24)
    ax.set_ylabel("Number of cores operating at full power",fontsize=24)
    ax.set_title("Number of known cores on at each day in the experiment",fontsize=32)
    ax.set_ylim([0,3])
    ax.grid(True)
    plt.show()

def Plot_KnownPercentOffDays(GeneratedExperiment):
    fig=plt.figure()
    ax = fig.add_subplot(1,1,1)
    off_percent = []
    total_days = 0.
    num_offdays = 0.
    for j, status in enumerate(GeneratedExperiment.core_status_array):
        total_days+=1.
        if status != GeneratedExperiment.numknowncores:
            num_offdays += 1.
        off_percent.append(num_offdays * 100 / total_days)
    ax.plot(GeneratedExperiment.experiment_days, off_percent,
            color='m', marker = 'o', alpha=0.8, linestyle='none') 
    ax.set_xlabel("days")
    ax.set_ylabel("%days where a core is off up to this day")
    ax.set_title("% of off days given the day in the experiment")
    ax.set_ylim([0,101])
    plt.show()

def Plot_KnownRatioOnOffDays(GeneratedExperiment):
    fig=plt.figure()
    ax = fig.add_subplot(1,1,1)
    on_off_ratio = []
    num_ondays = 0.00001
    num_offdays = 0.00001
    for j, status in enumerate(GeneratedExperiment.core_status_array):
        if status == GeneratedExperiment.numknowncores:
            num_ondays += 1.
        else:
            num_offdays +=1.
        on_off_ratio.append(num_offdays / num_ondays)
    ax.plot(GeneratedExperiment.experiment_days, on_off_ratio,
            color='m', marker = 'o', alpha=0.8, linestyle='none') 
    ax.set_xlabel("days")
    ax.set_ylabel("Ratio of # off days/ # on days at this day")
    ax.set_title("On/Off ratio")
    ax.set_ylim([0,3])
    plt.show()

#Takes in the first type of experiment analysis and plots the average events
#per N days (N can be seen by calling Analysis.bin_choice) for when reactors
#Are on and when they are off
def Plot_Analysis1OnOff_poserr(Analysis):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(Analysis.binning_choices, Analysis.onday_avg, \
        xerr=0, yerr=Analysis.onday_stdev, marker='o', linestyle='none', \
        color='b', alpha=0.7, label='Both cores on')
    ax.errorbar(Analysis.binning_choices, Analysis.offday_avg, \
        xerr=0, yerr=Analysis.offday_stdev, marker='o', linestyle='none', \
        color='r', alpha=0.7, label='At least one core off')
    ax.set_xlabel("Days of data in a bin")
    ax.set_ylabel("Average IBDs/bin")
    ax.set_title("Average number of IBDs measured for different data binnings\n" + \
            "Total days in experiment: {} days".format(Analysis.totaldays))
    plt.legend([ax])
    plt.show()

#Same as above; in this case, error bars are shown as the square root of the
#Avg. IBDs per bin
def Plot_Analysis1OnOff(Analysis):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(Analysis.binning_choices, Analysis.onday_avg, \
        xerr=0, yerr=np.sqrt(Analysis.onday_avg), marker='o', linestyle='none', \
        color='g', alpha=0.7, label='Both cores on')
    ax.errorbar(Analysis.binning_choices, Analysis.offday_avg, \
        xerr=0, yerr=np.sqrt(Analysis.offday_avg), marker='o', linestyle='none', \
        color='m', alpha=0.7, label='At least one core off')
    ax.set_xlabel("Days of data in a bin")
    ax.set_ylabel("Average IBDs/bin")
    ax.set_title("Average number of IBDs measured for different data binnings\n" + \
            "Total days in experiment: {} days".format(Analysis.totaldays))
    plt.legend(loc = 2)
    plt.show()

def Plot_OnOffCumSum_A2(Analysis2,sitename="Boulby"):
    '''
    Takes in an Analysis2 subclass and plots the results from the 3Sigma
    studies for the current experiment fed into the Analysis2 call.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.axvline(x=Analysis2.currentexp_determination_day,color='r', \
            label=r'on > off by 3$\sigma$',linewidth=4)
    ax.errorbar(Analysis2.Current_Experiment.experiment_days, \
        Analysis2.onavg_cumul, xerr=0, yerr=Analysis2.onavg_cumul_unc, \
        marker='o', linestyle='none', color='g', alpha=0.7, label='Both cores on')
    ax.errorbar(Analysis2.Current_Experiment.experiment_days, \
        Analysis2.offavg_cumul, xerr=0, yerr=Analysis2.offavg_cumul_unc, \
        marker='o', linestyle='none', \
        color='m', alpha=0.7, label='One core off')
    ax.axhline(y=0,color='k')
    ax.set_xlabel("Day in WATCHMAN observation",fontsize=30)
    ax.set_ylabel("Average IBDs/day rate",fontsize=30)
    ax.set_title("IBD event rate for subdatasets at each observation day \n"+\
            "WATCHMAN %s site, Determination day = %i"%(sitename,Analysis2.currentexp_determination_day),
            fontsize=32)
    ax.grid(True,linewidth=1,color='k',linestyle=':',alpha=0.7)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(24)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(24)
    legend = plt.legend(loc=1,frameon=1,fontsize=18)
    frame = legend.get_frame()
    frame.set_facecolor("white")
    plt.show()

def Plot_OnOffDiff_A2(Analysis2,sitename=None):
    '''
    Takes in an Analysis2 subclass and plots the difference of the
    "Both cores on" and "one core off" data sets' cumulative sums on
    that day.  The uncertainty is the total uncertainty.  If no error
    bars, one of the data sets is still empty.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    days = list(cp.deepcopy(Analysis2.Current_Experiment.experiment_days))
    cumulunc = list(cp.deepcopy(Analysis2.tot_cumul_unc))
    high = cp.deepcopy(Analysis2.onavg_cumul)
    low = cp.deepcopy(Analysis2.offavg_cumul)
    del high[0:61]
    del low[0:61]
    del cumulunc[0:61]
    del days[0:61]
    high = np.array(high)
    low = np.array(low)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(days, \
        (high - low), xerr=0, \
        yerr=cumulunc, \
        marker='o', linestyle='none', color='b', alpha=0.7, label='On - Off')
    ax.axvline(x=Analysis2.currentexp_determination_day,color='r', \
            label=r'(on - off > 0) by 3$\sigma$')
    ax.axhline(y=0,color='k')
    ax.set_xlabel("Days since experiment started")
    ax.set_ylabel("Average IBDs/day rate")
    ax.set_title("Average on-off IBDs/day at WATCHMAN " + str(sitename) + \
            "Site \n" + \
            "Determination day = {}".format(Analysis2.currentexp_determination_day))
    ax.grid(True)
    plt.legend(loc = 2)
    plt.show()

def Plot_OnOffCumSum_A1(Analysis1):
    '''
    Plots results from calling the ExperimentalAnalysis11 class.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(Analysis1.csum_numdays, Analysis1.csum_on, \
        xerr=0, yerr=np.sqrt(Analysis1.csum_on), marker='o', linestyle='none', \
        color='g', alpha=0.7, label='Both cores on')
    ax.errorbar(Analysis1.csum_numdays, Analysis1.csum_off, \
        xerr=0, yerr=np.sqrt(Analysis1.csum_off), marker='o', linestyle='none', \
        color='m', alpha=0.7, label='At least one core off')
    ax.axvline(x=Analysis1.currentexp_determination_day,color='k', \
            label=r'on > off by 3$\sigma$')
    ax.set_xlabel("Number of days of IBD data")
    ax.set_ylabel("IBD candidates")
    ax.set_title("Number of days of data collected\n" + \
            "Determination day = {}".format(Analysis1.currentexp_determination_day))
    plt.legend(loc = 2)
    plt.show()

def Plot_NRBackgrounds(GeneratedExperiment):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
        xerr=0, yerr=GeneratedExperiment.NR_bkg_unc, marker='o', linestyle='none', \
        color='g', alpha=0.7)
    ax.axhline(y=GeneratedExperiment.avg_NRbackground,color='k')
    ax.set_xlabel("days")
    ax.set_ylabel("Candidate events")
    ax.set_title("Non-Reactor Backgrounds for WATCHMAN \n" + \
            'Event binning = ' + str(GeneratedExperiment.resolution) + 'days')
    plt.show()


def Plot_Signal(GeneratedExperiment,showtruthmap=True):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.events, \
            linestyle='none', color='red', alpha=0.8,markersize=5,marker='o')
    if showtruthmap:
        mm._AddOpMap(GeneratedExperiment.schedule_dict,ax)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(24)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(24)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 , box.width*0.9, box.height])
    ax.legend(loc=2, bbox_to_anchor=(1, 0.5))
    ax.set_xlabel("Experiment day",fontsize=30)
    ax.set_ylabel("Candidate events",fontsize=30)
    ax.set_title("Total IBD candidates for one statistically \n"+\
            "generated WATCHMAN experiment", fontsize=32)

    plt.show()

def Plot_Cores(GeneratedExperiment):
    fig = plt.figure()
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)
    ax1.errorbar(GeneratedExperiment.experiment_days, GeneratedExperiment.known_core_events, \
            xerr=0, yerr=np.sqrt(GeneratedExperiment.known_core_events), \
            marker = 'o', linestyle='none', color='m', alpha=0.7)
    ax2.errorbar(GeneratedExperiment.experiment_days, GeneratedExperiment.unknown_core_events, \
            xerr=0, yerr=np.sqrt(GeneratedExperiment.unknown_core_events), \
            marker = 'o', linestyle='none', color='orange', alpha=0.9)
    ax1.set_xlabel("days")
    ax2.set_xlabel("days")
    ax1.set_ylabel("Candidate events")
    ax2.set_ylabel("Candidate events")
    ax1.set_title("Background reactor candidate events in WATCHMAN")
    ax2.set_title("Signal reactor candidate events in WATCHMAN")
    plt.show()


