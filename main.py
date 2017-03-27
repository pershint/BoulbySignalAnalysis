#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import optparse
import sys
import lib.playDarts as pd
import lib.DBParse as dp
import graph.Histogram as h
import lib.Exp_Generator as eg
import lib.Analysis as a
import graph.Exp_Graph as gr
import numpy as np
import lib.ExpFitting as ef

parser = optparse.OptionParser()
parser.add_option("--debug",action="store_true",default="False")
parser.add_option("-S","--site",action="store",dest="site", \
        default="Boulby",help="Input which experimental site you are" + \
            "assuming for WATCHMAN (Boulby and Fairport implemented")
parser.add_option("-r","--resolution",action="store",dest="resolution", \
        type="int",default=30,help="Specify the number of days per bin " +\
        "for the produced experimental data")
parser.add_option("-u","--uptime",action="store",dest="uptime", \
        type="int",default=180,help="Specify the uptime, in days, " + \
        "for a reactor between outages")
parser.add_option("-d","--days",action="store",dest="days", \
        type="int",default=1080,help="Total number of days of candidate " + \
        "events produced")
parser.add_option('-t',"--offtime",action="store",dest="offtime", \
        type="int",default=16,help="Average # days that a reactor is off for " + \
        "maintenance")
parser.add_option('-e','--efficiency',action="store",dest="efficiency", \
        type="float",default=None,help="Detector efficiency (0.2,0.4,0.6,0.8,"+\
        "1.0 only currently implemented")
parser.add_option('-p','--photocov',action="store",dest="pc", \
        type="float",default=None,help="Photocoverage of WATCHMAN" + \
        "to use(0.25 only implemented)")

(options,args) = parser.parse_args()
PHOTOCOVERAGE = options.pc
DETECTION_EFF = options.efficiency
SITE = options.site
RESOLUTION = options.resolution  #In days
OFF_TIME = options.offtime       #In days
UP_TIME = options.uptime         #In days
TOTAL_RUN = options.days    #In Days (NOTE: If not divisible by RESOLUTION, will round
                 #down to next lowest number divisible by RESOLUTION)



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

    #------------- BEGIN DEMO OF HOW STATS ARE FLUCTUATED ----------#
    title = "Events fired distribution for " + str(cores["known_core"]) + "in a single" + \
        "bin of width " + str(RESOLUTION) + "days"
    #StatFlucDemo(Boulby.signals[KNOWN_CORE]*RESOLUTION, title)
    #------------- END DEMO OF HOW STATS ARE FLUCTUATED ------------#

    Run1 = eg.ExperimentGenerator(signals, OFF_TIME, UP_TIME, RESOLUTION, cores, \
        TOTAL_RUN)
    Run1.show()  #Shows output of some experiment run details
#    gr.Plot_NRBackgrounds(Run1)
#    gr.Plot_Signal(Run1)
#    gr.Plot_Cores(Run1)
#    gr.Plot_ReacOnOff(Run1)
#    h.hPlot_CoresOnAndOffHist(Run1)

    #Try out the new ExperimentAnalyzer class
    binning_choices = np.arange(3,30,1)
    doReBin_Analysis = False
    Analysis2 = a.Analysis2(SITE)
    Analysis2(Run1)
    gr.Plot_OnOffCumSum_A2(Analysis2)
    gr.Plot_OnOffDiff_A2(Analysis2)
    #Now, run 100 experiments, determination days from each experiment,
    #And fill a histogram
    experiments = np.arange(0,10000,1)
    determination_days = []

    for experiment in experiments:
        Run = eg.ExperimentGenerator(signals, OFF_TIME, UP_TIME, RESOLUTION, cores, \
            TOTAL_RUN)
        Analysis2(Run)
    print("# EXP. WITH NO DETERMINATION IN TIME ALOTTED: \n")
    print(Analysis2.num_nodetermine)
    h.hPlot_Determ_InExpDays(Analysis2.determination_days, \
            np.max(Analysis2.determination_days),0.5, \
            (np.max(Analysis2.determination_days) + 0.5))

    #Takes the determination day spread filled in Analysis2 and fits it to a 
    #Poisson distribution
    TITLE = str('# Days of data needed to distinguish on/off reactor states' + \
            '(PC = {0}, off-time = {1} days)'.format(PHOTOCOVERAGE,OFF_TIME))
    c1, h = ef.PoissonFit(TITLE,Analysis2.determination_days)
    c1.Draw()
    h.Draw()
