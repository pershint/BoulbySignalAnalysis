#Functions for graphing different properties of a generated experiment

import numpy as np
import matplotlib.pyplot as plt

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


