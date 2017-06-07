#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import optparse
import json
import os.path
import sys
import lib.playDarts as pd
import lib.DBParse as dp
import graph.Histogram as h
import lib.Exp_Generator as eg
import lib.Analysis as a
import graph.Exp_Graph as gr
import numpy as np
#import lib.ExpFitting as ef

basepath = os.path.dirname(__file__)
savepath = os.path.abspath(os.path.join(basepath,"jobresults"))


parser = optparse.OptionParser()
parser.add_option("--debug",dest="debug",action="store_true",default="False")
parser.add_option("-S","--site",action="store",dest="site", \
        default="Boulby",help="Input which experimental site you are" + \
            "assuming for WATCHMAN (Boulby and Fairport implemented")
parser.add_option("-k","--killreacs",action="store",dest="killreacs", \
        type="int",default=None,help="If defined, both reactors will" + \
        "shut down for all days following the input day")
parser.add_option("-r","--resolution",action="store",dest="resolution", \
        type="int",default=1,help="Specify the number of days per bin " +\
        "for the produced experimental data")
parser.add_option("-u","--uptime",action="store",dest="uptime", \
        type="int",default=1080,help="Specify the uptime, in days, " + \
        "for a reactor between outages")
parser.add_option("-d","--days",action="store",dest="days", \
        type="int",default=1800,help="Total number of days of candidate " + \
        "events produced")
parser.add_option('-t',"--offtime",action="store",dest="offtime", \
        type="int",default=60,help="Average # days that a reactor is off for " + \
        "maintenance")
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
schedule_dict = {}  #All entries given in days
schedule_dict["OFF_TIME"] = options.offtime
schedule_dict["UP_TIME"] = options.uptime
schedule_dict["KILL_DAY"] = options.killreacs
schedule_dict["TOTAL_RUN"] = options.days


def StatFlucDemo(lamb, title):
    '''
    Gives a quick demo of the distribution  given when
    performing a random shoot of a variable.
    '''
    #Fire 1000 days to get the afterage nu/day histogram for the known Core
    events = pd.RandShoot_p(lamb,1000)
    h.hPlot_SignalHistogram(title, events, 60, -0.5, 60.5)

if __name__=='__main__':
    cores = {}
    if SITE=="Boulby":
        cores["known_core"] = "Core_1"
        cores["unknown_cores"] = ["Core_2"]
    if SITE=="Fairport":
        cores["known_core"] = "Core_1"
        cores["unknown_cores"] = []
    
    if PHOTOCOVERAGE is not None and DETECTION_EFF is not None:
        print("CHOOSE EITHER A PHOTOCOVERAGE OR EFFICIENCY, NOT BOTH.")
        sys.exit(0)
    elif PHOTOCOVERAGE is not None:
        signals = dp.Signals_PC(PHOTOCOVERAGE, SITE)
        print(signals.signals)
    elif DETECTION_EFF is not None:
        signals = dp.Signals(DETECTION_EFF, SITE)
        print(signals.signals)
    elif DETECTION_EFF is None and PHOTOCOVERAGE is None:
        print("CHOOSE A PHOTOCOVERAGE OR EFFICIENCY YO")
        sys.exit(0)

    #------------- BEGIN DEMO OF HOW STATS ARE FLUCTUATED ----------#
    title = "Events fired distribution for " + str(cores["known_core"]) + "in a single" + \
        "bin of width " + str(RESOLUTION) + "days"
    #StatFlucDemo(Boulby.signals[KNOWN_CORE]*RESOLUTION, title)
    #------------- END DEMO OF HOW STATS ARE FLUCTUATED ------------#

    Run1 = eg.ExperimentGenerator(signals, schedule_dict, RESOLUTION, cores)
    if DEBUG is True:
        Run1.show()  #Shows output of some experiment run details
#    gr.Plot_NRBackgrounds(Run1)
#    gr.Plot_Signal(Run1)
#    gr.Plot_Cores(Run1)
#    gr.Plot_ReacOnOff(Run1)
#    h.hPlot_CoresOnAndOffHist(Run1)

    Analysis2 = a.Analysis2(SITE)
    if DEBUG is True:
        #Try out the new ExperimentAnalyzer class
        Analysis2(Run1)
        gr.Plot_OnOffCumSum_A2(Analysis2)
        gr.Plot_OnOffDiff_A2(Analysis2)
    #Now, run 100 experiments, determination days from each experiment,
    #And fill a histogram
    experiments = np.arange(0,100,1)

    for experiment in experiments:
        Run = eg.ExperimentGenerator(signals, schedule_dict, RESOLUTION, cores)
        Analysis2(Run)
    determination_data = Analysis2.determination_days
    datadict = {"Site": SITE,"pc":PHOTOCOVERAGE, "schedule_dict": schedule_dict,
            "determination_days":determination_data,"no3sigmadays":Analysis2.num_nodetermine}
    with open(savepath + "/results_j"+str(jn)+".json","w") as datafile:
        json.dump(datadict,datafile,sort_keys=True,indent=4)
    if DEBUG is True:
        print("# EXP. WITH NO DETERMINATION IN TIME ALOTTED: \n")
        print(Analysis2.num_nodetermine)
        h.hPlot_Determ_InExpDays(Analysis2.determination_days, \
                np.max(Analysis2.determination_days),0.5, \
                (np.max(Analysis2.determination_days) + 0.5))

        #Takes the determination day spread filled in Analysis2 and fits it to a 
        #Poisson distribution
        TITLE = str('# Days of data needed to distinguish on/off reactor states' + \
                '(PC = {0}, off-time = {1} days)'.format(PHOTOCOVERAGE,OFF_TIME))
        #c1, h = ef.PoissonFit(TITLE,Analysis2.determination_days)
        #c1.Draw()
        h.Draw()
