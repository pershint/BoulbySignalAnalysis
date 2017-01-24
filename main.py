#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN

import lib.playDarts as pd
import lib.DBParse as dp
import lib.Histogram as h
import numpy as np

DETECTION_EFF = 1
KNOWN_CORE = 'Core_1'
UNKNOWN_CORE = 'Core_2'
RESOLUTION = 8  #In days
OFF_TIME = 15   #In days

if __name__=='__main__':
    Boulby = dp.BoulbySignals(DETECTION_EFF)
    print(Boulby.signals)
    #Fire 1000 days to get the afterage nu/day histogram for the known Core
    events = pd.RandShoot(Boulby.signals[KNOWN_CORE], np.sqrt(Boulby.signals[KNOWN_CORE]), \
            1000)
    Poiss_events = np.random.poisson(Boulby.signals[KNOWN_CORE], 1000)
    h.Plot_SignalHistogram(KNOWN_CORE, events, 20, 0.0, 8.0)
    h.Plot_SignalHistogram(KNOWN_CORE, Poiss_events, 20, 0.0, 8.0)
