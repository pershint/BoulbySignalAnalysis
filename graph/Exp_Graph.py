#Functions for graphing different properties of a generated experiment

import numpy as np
import matplotlib.pyplot as plt

def Plot_NRBackgrounds(GeneratedExperiment):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.plot(GeneratedExperiment.experiment_day, GeneratedExperiment.NR_bkg, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(GeneratedExperiment.experiment_day, GeneratedExperiment.NR_bkg, \
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
    #ax.plot(GeneratedExperiment.experiment_day, GeneratedExperiment.events, \
    #        'ro', color='blue', alpha=0.8)
    ax.errorbar(GeneratedExperiment.experiment_day, GeneratedExperiment.events, \
        xerr=0, yerr=GeneratedExperiment.events_unc, marker='o',\
        linestyle='none',color='r', alpha=0.7)
    ax.axhline(y=GeneratedExperiment.avg_NRbackground,color='k')
    ax.set_xlabel("days")
    ax.set_ylabel("Candidate events")
    ax.set_title("Total signal for WATCHMAN, efficiency = " + \
            str(GeneratedExperiment.efficiency) + '\n' + \
            'Event binning = ' + str(GeneratedExperiment.resolution) + 'days')
    plt.show()
