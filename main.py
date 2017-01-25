#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import optparse
import lib.playDarts as pd
import lib.DBParse as dp
import graph.Histogram as h
import lib.Exp_Generator as eg
import graph.Exp_Graph as gr
import numpy as np


parser = optparse.OptionParser()
parser.add_option("--debug",action="store_true",default="False")
parser.add_option("-r","--resolution",action="store",dest="resolution", \
        type="int",default=30,help="Specify the number of days per bin " +\
        "for the produced experimental data")
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
KNOWN_CORE = 'Core_1'
UNKNOWN_CORE = 'Core_2'
RESOLUTION = options.resolution  #In days
OFF_TIME = options.offtime       #In days
TOTAL_RUN = options.days    #In Days (NOTE: If not divisible by RESOLUTION, will round
                 #down to next lowest number divisible by RESOLUTION)



def StatFlucDemo(mu, sigma, title):
    '''
    Gives a quick demo of the distribution  given when
    performing a random shoot of a variable.
    '''
    #Fire 1000 days to get the afterage nu/day histogram for the known Core
    events = pd.RandShoot(mu,sigma, 1000)
    h.Plot_SignalHistogram(title, events, 50, 0, 60)

if __name__=='__main__':
    Boulby = dp.BoulbySignals(DETECTION_EFF)
    print(Boulby.signals)

    #------------- BEGIN DEMO OF HOW STATS ARE FLUCTUATED ----------#
    title = "Events fired distribution for " + str(KNOWN_CORE) + "in a single" + \
        "bin of width " + str(RESOLUTION) + "days"
    StatFlucDemo(Boulby.signals[KNOWN_CORE]*RESOLUTION, \
            np.sqrt(Boulby.signals[KNOWN_CORE]*RESOLUTION), title)
    #------------- END DEMO OF HOW STATS ARE FLUCTUATED ------------#

    Num_data_bins = TOTAL_RUN / RESOLUTION
    Run1 = eg.ExperimentGenerator(Boulby, OFF_TIME, RESOLUTION, UNKNOWN_CORE, \
        100)
    #Run1.show()  #Shows output of some experiment run details
    gr.Plot_NRBackgrounds(Run1)
    gr.Plot_Signal(Run1)

