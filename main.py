#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import optparse
import json
import os.path
import sys
import lib.playDarts as pd
import lib.Exp_Generator as eg
import lib.Analysis as a
import numpy as np
#import lib.ExpFitting as ef

basepath = os.path.dirname(__file__)
savepath = os.path.abspath(os.path.join(basepath,"jobresults"))


parser = optparse.OptionParser()
parser.add_option("--debug",dest="debug",action="store_true",default="False")
parser.add_option("-k","--killreacs",action="store",dest="killreacs", \
        type="int",default=None,help="If defined, both reactors will" + \
        "shut down for all days following the input day")
parser.add_option('-e','--efficiency',action="store",dest="efficiency", \
        type="float",default=None,help="Detector efficiency (0.2,0.4,0.6,0.8,"+\
        "1.0 only currently implemented")
parser.add_option('-p','--photocov',action="store",dest="pc", \
        type="float",default=None,help="Photocoverage of WATCHMAN" + \
        "to use(0.25 only implemented)")
parser.add_option('-b','--buffersize',action="store",dest="bufsize", \
        type="float",default=1.5,help="Specify buffer size in meters")
parser.add_option('-a','--activity',action="store", dest="activity", \
        type="string",help="Specify what type of PMTs you want the signal"+\
        "/background for (normal_activity, 5050mix, or low_activity)")
parser.add_option('-c','--schedule',action="store_true",dest="schedule", \
        default="False",help="Search for difference in IBD numbers in known"+\
        "reactor on and reactor off data sets")
parser.add_option('-f','--poisfit',action="store_true",dest="posfit", \
        default="False",help="Fit a poisson to 'rector off' data for known reactors")
parser.add_option('-s','--SPRT',action="store_true",dest="sprt", \
        default="False",help="Run an SPRT over all on days for known reactors")
parser.add_option('-l','--Kalman',action="store_true",dest="kalman", \
        default="False",help="Run the Kalman Filter probability test on"+\
        "each statistical experiment generated")
parser.add_option('-j','--jobnum',action="store",dest="jobnum", \
        type="int",default=0,help="Job number (for saving data/grid use)")

(options,args) = parser.parse_args()
DEBUG = options.debug
SPRT = options.sprt
KALMAN = options.kalman
POISFIT = options.posfit
SCHED = options.schedule
jn = options.jobnum
if options.pc is not None:
    PHOTOCOVERAGE = options.pc
if options.activity is not None:
    PMTTYPE = options.activity
if options.bufsize is not None:
    BUFFERSIZE = options.bufsize

import lib.config.config as c
if DEBUG is True:
    import graph.Histogram as h
    import graph.Exp_Graph as gr
    import matplotlib.pyplot as plt
if __name__=='__main__':
    print(str(c.signals.signals)) 
    #Run once, add the maintenance and core shutoffs to schedule_dict
    Run1 = eg.ExperimentGenerator(c.signals, c.schedule_dict, c.RESOLUTION, \
            c.cores)
    #FIXME: A bit dirty adding this in after the fact and not in config..
    c.schedule_dict["MAINTENANCE_STARTDAYS"] = Run1.core_maintenance_startdays
    c.schedule_dict["SHUTDOWN_STARTDAYS"] = Run1.core_shutoff_startdays
    if DEBUG is True:
        Run1.show()  #Shows output of some experiment run details
        #gr.Plot_NRBackgrounds(Run1)
        #gr.Plot_Signal(Run1)
        #gr.Plot_Cores(Run1)
        gr.Plot_KnownReacOnOff(Run1)
        gr.Plot_AllReacOnOff(Run1)
        gr.Plot_KnownRatioOnOffDays(Run1)
        gr.Plot_KnownPercentOffDays(Run1)
        h.hPlot_CoresOnAndOffHist(Run1)
        ScheduleAnalysis = a.ScheduleAnalysis(c.SITE)
        #Try out the new ExperimentAnalyzer class
        ScheduleAnalysis(Run1)
        gr.Plot_OnOffCumSum_A2(ScheduleAnalysis)
        gr.Plot_OnOffDiff_A2(ScheduleAnalysis)

    
    #Initialize our analysis class.  The scheduleanalysis takes in multiple
    #Experiments generated and holds statistics regarding at what day into
    #The experiment WATCHMAN observes a 3sigma difference in the "reactor on"
    #and "reactor off" days of data
    ScheduleAnalysis = a.ScheduleAnalysis(c.SITE)
    UnknownCoreAnalysis = a.UnknownCoreAnalysis(c.SITE)
    SPRTAnalysis = a.SPRTAnalysis(c.SITE)
    KalmanAnalysis = a.KalmanFilterAnalysis(c.SITE)
    #Datadict object will save the output configuration and results of analysis
    datadict = {"Site": c.SITE,"pc":c.PHOTOCOVERAGE,"buffersize":c.BUFFERSIZE, 
            "pmt_type":c.PMTTYPE,"schedule_dict": c.schedule_dict, "Analysis": None}
    experiments = np.arange(0,c.NEXPERIMENTS,1)
    
    if KALMAN is True:
        datadict["Analysis"] = "KALMAN"
        for experiment in experiments:
            SingleRun = eg.ExperimentGenerator(c.signals, c.schedule_dict, c.RESOLUTION, \
                    c.cores)
            KalmanAnalysis(SingleRun)
        #if DEBUG is True:
        datadict["PL_distributions"] = KalmanAnalysis.PL_distributions
        datadict["PH_distributions"] = KalmanAnalysis.PH_distributions
        if DEBUG is True:
            print("SHOWING PLOT OF FIRST EXPERIMENT'S PROBABILITY TRACKING")
            PL_days = KalmanAnalysis.PL_distributions[0]
            PH_days = KalmanAnalysis.PH_distributions[0]
            Exp_day = KalmanAnalysis.experiment_days
            plt.plot(Exp_day, PL_days, color='b', label='PL')
            plt.plot(Exp_day, PH_days, color='r', label='PH')
            plt.legend(loc=1)
            plt.show()
    if SPRT is True:
        datadict["Analysis"] = "SPRT"
        for experiment in experiments:
            SingleRun = eg.ExperimentGenerator(c.signals, c.schedule_dict, c.RESOLUTION, \
                    c.cores)
            SPRTAnalysis(SingleRun)
        datadict["above_null_days"] = SPRTAnalysis.SPRT_accdays
        datadict["below_null_days"] = SPRTAnalysis.SPRT_rejdays
        datadict["no_hypothesis"] = SPRTAnalysis.SPRT_unccount
        if DEBUG is True:
            plt.plot(SPRTAnalysis.SPRTresultday, SPRTAnalysis.SPRTresult, \
                    linestyle='none', marker='o', label='# IBD Candidates')
            plt.plot(SPRTAnalysis.SPRTresultday, SPRTAnalysis.SPRTaccbound, \
                    linestyle='none', marker='o', color = 'g', label=r'Accept $\mu+3\sigma_{\mu}$')
            plt.plot(SPRTAnalysis.SPRTresultday, SPRTAnalysis.SPRTrejbound, \
                    linestyle='none', marker='o', color = 'r', label=r"Accept $\mu-3\sigma_{\mu} '$")
            if c.schedule_dict['KILL_DAYS'] is not None:
                for day in c.schedule_dict['KILL_DAYS']:
                    plt.axvline(day, linewidth = 3, color='m', label='Core shutdown')
            plt.plot(SPRTAnalysis.SPRTresultday, SPRTAnalysis.SPRTtestpredict, \
                    linewidth=3, color='k',label='Avg. prediction for # IBDs')
            plt.title("SPRT Result for generated experiment using on data \n" + \
                    "for known core")
            plt.xlabel("Day in experiment")
            plt.ylabel("Number of IBD candidates")
            plt.legend(loc=2)
            plt.grid()
            plt.show()
            #print("NUMBER OF ACCEPTANCE DAYS: " + str(len(SPRTAnalysis.SPRT_accdays)))
            #plt.hist(SPRTAnalysis.SPRT_accdays,np.max(SPRTAnalysis.SPRT_accdays))
            #plt.show()
            print("NUMBER OF REJECTION DAYS: " + str(len(SPRTAnalysis.SPRT_rejdays)))
            if len(SPRTAnalysis.SPRT_rejdays) != 0:
                plt.hist(SPRTAnalysis.SPRT_rejdays,np.max(SPRTAnalysis.SPRT_rejdays))
                plt.show()
            print("NUMBER OF NO CONCLUSIONS: " + str(SPRTAnalysis.SPRT_unccount))

    if POISFIT is True:
        datadict["Analysis"] = "POISSON_FIT"
        for experiment in experiments:
            Run = eg.ExperimentGenerator(c.signals, c.schedule_dict, c.RESOLUTION, \
                    c.cores)
            UnknownCoreAnalysis(Run)
        print("NUM FAILED FITS: " + str(UnknownCoreAnalysis.num_failfits))
        plt.hist(UnknownCoreAnalysis.csndf_offbinfits, 40, range=(0.0,8.0))
        plt.xlabel("Distribution of Chi-Squared/NDF for each 1800 day experiment")
        plt.title("Chi squared/NDF")
        plt.show()
        plt.hist(UnknownCoreAnalysis.mu_offbinfits, 30, range=(0.0,6.0))
        plt.xlabel("Distribution of Poisson average for each 1800 day experiment")
        plt.title(r"$\mu$ best fit")
        plt.show()
    if SCHED is True:
        datadict["Analysis"] = "ONOFF_DIFFERENCE"
        for experiment in experiments:
            Run = eg.ExperimentGenerator(c.signals, c.schedule_dict, c.RESOLUTION, \
                    c.cores)
            ScheduleAnalysis(Run)
            datadict["determination_days"] = ScheduleAnalysis.determination_days
            datadict["no3sigmadays"] = ScheduleAnalysis.num_nodetermine
            datadict["num3siginarow"] = ScheduleAnalysis.num3siginarow
        if DEBUG is True:
            print("# EXP. WITH NO DETERMINATION IN TIME ALOTTED: \n")
            print(ScheduleAnalysis.num_nodetermine)
            h.hPlot_Determ_InExpDays(ScheduleAnalysis.determination_days, \
                    np.max(ScheduleAnalysis.determination_days),0.5, \
                    (np.max(ScheduleAnalysis.determination_days) + 0.5))
    
    #The Analysis is complete.  Save the results from the Schedule Analysis
    with open(savepath + "/results_j"+str(jn)+".json","w") as datafile:
        json.dump(datadict,datafile,sort_keys=True,indent=4)


