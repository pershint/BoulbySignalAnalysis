#Functions for graphing different properties of a generated experiment

import numpy as np
import matplotlib.pyplot as plt


def Plot_ReacOnOff(GeneratedExperiment):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.unknown_core_onoffdays,
            color='k', alpha=0.8)
    ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.known_core_onoffdays,
            color='b', alpha=0.8) 
    ax.set_xlabel("days")
    ax.set_ylabel("Reactor state (1-on, 0-off)")
    ax.set_ylim([0,2])
    ax.set_title("Reactor core states during experiment (black - unknown core, " + \
            'blue - known core)')
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
        color='r', alpha=0.7, label='One core off')
    ax.set_xlabel("Days of data in a bin")
    ax.set_ylabel("Average IBDs/bin")
    ax.set_title("Average number of IBDs measured for different data binnings\n" + \
            "Total days in experiment: {} days".format(Analysis.totaldays))
    plt.legend(loc = 2)
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
        color='m', alpha=0.7, label='One core off')
    ax.set_xlabel("Days of data in a bin")
    ax.set_ylabel("Average IBDs/bin")
    ax.set_title("Average number of IBDs measured for different data binnings\n" + \
            "Total days in experiment: {} days".format(Analysis.totaldays))
    plt.legend(loc = 2)
    plt.show()

def Plot_OnOffCumSum(Analysis):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(Analysis.csum_numdays, Analysis.csum_on, \
        xerr=0, yerr=np.sqrt(Analysis.csum_on), marker='o', linestyle='none', \
        color='g', alpha=0.7, label='Both cores on')
    ax.errorbar(Analysis.csum_numdays, Analysis.csum_off, \
        xerr=0, yerr=np.sqrt(Analysis.csum_off), marker='o', linestyle='none', \
        color='m', alpha=0.7, label='One core off')
    ax.set_xlabel("Number of days of IBD data")
    ax.set_ylabel("IBD candidates")
    ax.set_title("Number of days of data collected\n" + \
            "Efficiency = {}".format(Analysis.Current_Experiment.efficiency))
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
    ax.set_title("Non-Reactor Backgrounds for WATCHMAN, efficiency = " + \
            str(GeneratedExperiment.efficiency) + '\n' + \
            'Event binning = ' + str(GeneratedExperiment.resolution) + 'days')
    plt.show()


def Plot_Signal(GeneratedExperiment):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_days, GeneratedExperiment.events, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(GeneratedExperiment.experiment_days, GeneratedExperiment.events, \
        xerr=0, yerr=GeneratedExperiment.events_unc, marker='o',\
        linestyle='none',color='r', alpha=0.7)
    ax.axhline(y=GeneratedExperiment.avg_NRbackground,color='k')
    ax.set_xlabel("days")
    ax.set_ylabel("Candidate events")
    ax.set_title("Total signal for WATCHMAN, efficiency = " + \
            str(GeneratedExperiment.efficiency) + '\n' + \
            'Event binning = ' + str(GeneratedExperiment.resolution) + 'days')
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


