#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import json
import os.path
import sys
import lib.DBParse as dp
import lib.playDarts as pd
import lib.Exp_Generator as eg
import lib.Analysis as a
import lib.ArgParser as ap
import numpy as np

basepath = os.path.dirname(__file__)
savepath = os.path.abspath(os.path.join(basepath,"jobresults"))

DEBUG = ap.DEBUG
SPRT = ap.SPRT 
KALMAN = ap.KALMAN 
FORWARDBACKWARD = ap.FORWARDBACKWARD 
WINDOW = ap.WINDOW
POISFIT = ap.POISFIT
DWELLTIME = ap.DWELLTIME
jn = ap.jn
PHOTOCOVERAGE = ap.PHOTOCOVERAGE
PMTTYPE = ap.PMTTYPE
BUFFERSIZE = ap.BUFFERSIZE


import lib.config.schedule_config as c
import lib.config.DBConfig as dbc

if DEBUG is True:
    import graph.Histogram as h
    import graph.Exp_Graph as gr
    import matplotlib.pyplot as plt


if __name__=='__main__':
    
    signal_loader={}
    signal_loader= dp.Signals_PC(dbc.PHOTOCOVERAGE,dbc.PMTTYPE,dbc.BUFFERSIZE, dbc.SITE)
    if dbc.PMT_ORIENTATION is not None:
        signal_loader.set_orientation(dbc.PMT_ORIENTATION)
    if dbc.HAS_SHIELDS is not None:
        signal_loader.set_shields(dbc.HAS_SHIELDS)
    signal_loader.load_signal_dict()
    print("SIGNALS LOADED: " + str(signal_loader.signals)) 
    
    #Run once, add the maintenance and core shutoffs to schedule_dict
    Run1 = eg.ExperimentGenerator(signal_loader, c.schedule_dict, c.RESOLUTION, \
            dbc.cores)
    #FIXME: A bit dirty adding this in after the fact and not in config..
    c.schedule_dict["MAINTENANCE_STARTDAYS"] = Run1.core_maintenance_startdays
    c.schedule_dict["SHUTDOWN_STARTDAYS"] = Run1.core_shutoff_startdays
    if DEBUG is True:
        Run1.show()  #Shows output of some experiment run details
        #gr.Plot_NRBackgrounds(Run1)
        gr.Plot_Signal(Run1,showtruthmap=False)
        gr.Plot_Signal(Run1)
        #gr.Plot_Cores(Run1)
        gr.Plot_KnownReacOnOff(Run1)
        gr.Plot_AllReacOnOff(Run1)
        gr.Plot_KnownRatioOnOffDays(Run1)
        gr.Plot_KnownPercentOffDays(Run1)
        h.hPlot_CoresOnAndOffHist(Run1)
        ScheduleAnalysis = a.ScheduleAnalysis()
        #Try out the new ExperimentAnalyzer class
        ScheduleAnalysis(Run1)
        gr.Plot_OnOffCumSum_A2(ScheduleAnalysis)
        gr.Plot_OnOffDiff_A2(ScheduleAnalysis)

    
    #Initialize our analysis class.  The scheduleanalysis takes in multiple
    #Experiments generated and holds statistics regarding at what day into
    #The experiment WATCHMAN observes a 3sigma difference in the "reactor on"
    #and "reactor off" days of data
    ScheduleAnalysis = a.ScheduleAnalysis()
    UnknownCoreAnalysis = a.UnknownCoreAnalysis()
    SPRTAnalysis = a.SPRTAnalysis()
    KalmanAnalysis = a.KalmanFilterAnalysis()
    ForwardBackwardAnalysis = a.ForwardBackwardAnalysis()
    SlidingWindowAnalysis = a.SlidingWindowAnalysis()
    #Datadict object will save the output configuration and results of analysis
    datadict = {"Site": dbc.SITE,"pc":dbc.PHOTOCOVERAGE,"buffersize":dbc.BUFFERSIZE, 
            "pmt_type":dbc.PMTTYPE,"pmt_orientation":dbc.PMT_ORIENTATION,
            "has_shields":dbc.HAS_SHIELDS, "schedule_dict": c.schedule_dict, 
            "Analysis": None, "Signals": signal_loader.signals}
    experiments = np.arange(0,c.NEXPERIMENTS,1)
    training_experiments = np.arange(0,c.NTRAININGEXPTS,1)
    if WINDOW is True:
        datadict["Analysis"] = "WINDOW"
        datadict["Window_type"] = "average"
        datadict["Window_halfwidth"] = 30 
        SlidingWindowAnalysis.setHalfWidth(datadict["Window_halfwidth"])
        SlidingWindowAnalysis.setWindowType(datadict["Window_type"])
        for experiment in experiments:
            SingleRun = eg.ExperimentGenerator(signal_loader, c.schedule_dict, c.RESOLUTION, \
                    dbc.cores)
            SlidingWindowAnalysis(SingleRun)
        datadict['known_numcoreson'] = list(SingleRun.known_numcoreson)
        datadict['avg_distributions'] = SlidingWindowAnalysis.averaged_distributions
        #if DEBUG is True:
        if DEBUG is True:
            print("SHOWING PLOT OF FIRST EXPERIMENT'S SMOOTHING")
            avgdist = SlidingWindowAnalysis.averaged_distributions[0]
            avgdist_unc = SlidingWindowAnalysis.averaged_distributions_unc[0]
            Exp_day = SlidingWindowAnalysis.experiment_days
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            ax.plot(Exp_day, avgdist, marker='o',markersize=4, 
                    color='b', alpha=0.6,linestyle='none', label='Smoothed average')
            plt.title("WATCHMAN statistically generated data after undergoing\n"+\
                    "moving average window smoothing",fontsize=32)
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(24)
            ax.set_xlabel("Day at center of smoothing window",fontsize=30)
            ax.set_ylabel("Average window event rate (events/day)",fontsize=30)
            plt.legend(loc=1)
            plt.show()

    if FORWARDBACKWARD is True:
        datadict["Analysis"] = "FORWARDBACKWARD"
        datadict["schedule_dict_test"] = c.schedule_dict_test
        #Run a bunch of test experiments for training CL bands
        for experiment in training_experiments:
            SingleRun = eg.ExperimentGenerator(signal_loader, c.schedule_dict, c.RESOLUTION, \
                    dbc.cores)
            ForwardBackwardAnalysis(SingleRun,exptype="train")
        #Train the CL bands based on the assumption we have two cores both doing
        #outages at different times, with maintenance and large shutdowns
        ForwardBackwardAnalysis.TrainTheJudge(CL=0.90)
        for testexpt in experiments:
            TestRun = eg.ExperimentGenerator(signal_loader, c.schedule_dict_test, c.RESOLUTION, \
                        dbc.cores)
            #FIXME: Still dirty to add this here...
            c.schedule_dict_test["MAINTENANCE_STARTDAYS"] = TestRun.core_maintenance_startdays
            c.schedule_dict_test["SHUTDOWN_STARTDAYS"] = TestRun.core_shutoff_startdays
            ForwardBackwardAnalysis(TestRun,exptype="test")
        datadict['known_numcoreson'] = list(SingleRun.known_numcoreson)
        #if DEBUG is True:
        datadict["PH_dist_train"] = ForwardBackwardAnalysis.PH_dist_train
        datadict["PH_dist_test"] = ForwardBackwardAnalysis.PH_dist_test
        datadict["PH_CLhi"] = ForwardBackwardAnalysis.PH_CLhi
        datadict["PH_CLlo"] = ForwardBackwardAnalysis.PH_CLlo
        datadict["banddict"] = ForwardBackwardAnalysis.banddict
        datadict["probdistdict"] = ForwardBackwardAnalysis.probdistdict
        datadict["band_CL"] = ForwardBackwardAnalysis.CL
        datadict["Op_predictions"] = ForwardBackwardAnalysis.TestExpt_OpPredictions
        if DEBUG is True:
            print("SHOWING PLOT OF FIRST EXPERIMENT'S PROBABILITY TRACKING")
            PL_days = ForwardBackwardAnalysis.PL_dist_train[0]
            PH_days = ForwardBackwardAnalysis.PH_dist_train[0]
            Exp_day = ForwardBackwardAnalysis.experiment_days
            plt.plot(Exp_day, PL_days, color='b', label='PL')
            plt.plot(Exp_day, PH_days, color='r', label='PH')
            plt.legend(loc=1)
            plt.show()

    if KALMAN is True:
        datadict["Analysis"] = "KALMAN"
        for experiment in experiments:
            SingleRun = eg.ExperimentGenerator(signal_loader, c.schedule_dict, c.RESOLUTION, \
                    dbc.cores)
            KalmanAnalysis(SingleRun)
        #if DEBUG is True:
        datadict['known_numcoreson'] = list(SingleRun.known_numcoreson)
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
            SingleRun = eg.ExperimentGenerator(signal_loader, c.schedule_dict, c.RESOLUTION, \
                    dbc.cores)
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
                    "for known core (training data)")
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
            Run = eg.ExperimentGenerator(signal_loader, c.schedule_dict, c.RESOLUTION, \
                    dbc.cores)
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
    if DWELLTIME is True:
        datadict["Analysis"] = "3SIGMA_DWELL_TIME"
        for experiment in experiments:
            Run = eg.ExperimentGenerator(signal_loader, c.schedule_dict, c.RESOLUTION, \
                    dbc.cores)
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


