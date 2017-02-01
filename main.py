#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import optparse
import lib.playDarts as pd
import lib.DBParse as dp
import graph.Histogram as h
import lib.Exp_Generator as eg
import graph.Exp_Graph as gr
import numpy as np
import lib.ExpFitting as ef

parser = optparse.OptionParser()
parser.add_option("--debug",action="store_true",default="False")
parser.add_option("-r","--resolution",action="store",dest="resolution", \
        type="int",default=30,help="Specify the number of days per bin " +\
        "for the produced experimental data")
parser.add_option("-u","--uptime",action="store",dest="uptime", \
        type="int",default=180,help="Specify the uptime, in days, " + \
        "for a reactor between outages")
parser.add_option("-d","--days",action="store",dest="days", \
        type="int",default=3000,help="Total number of days of candidate " + \
        "events produced")
parser.add_option('-t',"--offtime",action="store",dest="offtime", \
        type="int",default=15,help="Average # days that a reactor is off for " + \
        "maintenance")
parser.add_option('-e','--efficiency',action="store",dest="efficiency", \
        type="float",default=0.8,help="Detector efficiency (0.2,0.4,0.6,0.8,"+\
        "1.0 only currently implemented")

(options,args) = parser.parse_args()

DETECTION_EFF = options.efficiency
KNOWN_CORE = 'Core_2'
UNKNOWN_CORE = 'Core_1'
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
    Boulby = dp.BoulbySignals(DETECTION_EFF)
    print(Boulby.signals)

    #------------- BEGIN DEMO OF HOW STATS ARE FLUCTUATED ----------#
    title = "Events fired distribution for " + str(KNOWN_CORE) + "in a single" + \
        "bin of width " + str(RESOLUTION) + "days"
    #StatFlucDemo(Boulby.signals[KNOWN_CORE]*RESOLUTION, title)
    #------------- END DEMO OF HOW STATS ARE FLUCTUATED ------------#

    Run1 = eg.ExperimentGenerator(Boulby, OFF_TIME, UP_TIME, RESOLUTION, UNKNOWN_CORE, \
        TOTAL_RUN)
    Run1.show()  #Shows output of some experiment run details
    gr.Plot_NRBackgrounds(Run1)
    gr.Plot_Signal(Run1)
    gr.Plot_Cores(Run1)

    #Take your total core events when a reactor is on and when a reactor is 
    #off and project them onto the y-axis
    h.hPlot_CoresOnAndOffHist(Run1)

    #Uncomment to use pyROOT to try and fit a poisson distribution
    #c1, h = ef.PoissonFit(Run1)
    #c1.Draw("al")
