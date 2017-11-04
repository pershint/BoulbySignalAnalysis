#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import optparse
import json
import os.path
import sys
import lib.playDarts as pd
import lib.DBParse as dp
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
parser.add_option('-j','--jobnum',action="store",dest="jobnum", \
        type="int",default=0,help="Job number (for saving data/grid use)")

(options,args) = parser.parse_args()
PHOTOCOVERAGE = options.pc
DEBUG = options.debug
DETECTION_EFF = options.efficiency
jn = options.jobnum
SITE = options.site
RESOLUTION = options.resolution  #In days

if DEBUG is True:
    import graph.Histogram as h
    import graph.Exp_Graph as gr

if __name__=='__main__':
    cores = {}
    if SITE=="Boulby":
        cores["known_cores"] = ['Core_1','Core_2']
        cores["unknown_cores"] = []
    if SITE=="Fairport":
        cores["known_cores"] = ["Core_1"]
        cores["unknown_cores"] = []
    
    #Run once, add the maintenance and core shutoffs to schedule_dict
    Run1 = eg.ExperimentGenerator(signals, schedule_dict, RESOLUTION, cores)
    #FIXME: A bit dirty adding this in after the fact and not in config..
    schedule_dict["MAINTENANCE_STARTDAYS"] = Run1.maintenance_startdays
    schedule_dict["SHUTDOWN_STARTDAYS"] = Run1.shutoff_startdays
    if DEBUG is True:
        Run1.show()  #Shows output of some experiment run details
        #gr.Plot_NRBackgrounds(Run1)
        #gr.Plot_Signal(Run1)
        #gr.Plot_Cores(Run1)
        gr.Plot_ReacOnOff(Run1)
        gr.Plot_RatioOnOffDays(Run1)
        gr.Plot_PercentOffDays(Run1)
        h.hPlot_CoresOnAndOffHist(Run1)
        ScheduleAnalysis = a.ScheduleAnalysis(SITE)
        #Try out the new ExperimentAnalyzer class
        ScheduleAnalysis(Run1)
        gr.Plot_OnOffCumSum_A2(ScheduleAnalysis)
        gr.Plot_OnOffDiff_A2(ScheduleAnalysis)

    #Now, run 100 experiments, determination days from each experiment,
    #And fill a histogram
    experiments = np.arange(0,100,1)
    ScheduleAnalysis = a.ScheduleAnalysis(SITE)
    for experiment in experiments:
        Run = eg.ExperimentGenerator(signals, schedule_dict, RESOLUTION, cores)
        ScheduleAnalysis(Run)
    determination_data = ScheduleAnalysis.determination_days
    datadict = {"Site": SITE,"pc":PHOTOCOVERAGE, "schedule_dict": schedule_dict,
            "determination_days":determination_data,"no3sigmadays":ScheduleAnalysis.num_nodetermine}
    with open(savepath + "/results_j"+str(jn)+".json","w") as datafile:
        json.dump(datadict,datafile,sort_keys=True,indent=4)
    if DEBUG is True:
        print("# EXP. WITH NO DETERMINATION IN TIME ALOTTED: \n")
        print(ScheduleAnalysis.num_nodetermine)
        h.hPlot_Determ_InExpDays(ScheduleAnalysis.determination_days, \
                np.max(ScheduleAnalysis.determination_days),0.5, \
                (np.max(ScheduleAnalysis.determination_days) + 0.5))
