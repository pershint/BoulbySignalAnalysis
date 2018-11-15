WATCHStat is a software package that is used to:
  - generate simulated WATCHMAN experiments assuming poisson statistics for signal/backgrounds
  - Run analyses on the simulated experiments to evaluate WATCHMAN's expected
    reactor monitoring performance
  - Plot the results of analyses for straightforward evaluation and presentation

The library is written in a way that Each step could be independently utilized
in someone else's code if desired.  However, the main.py provides a base
script for performing the first two steps and generating output that can be
used in the third step.

### USAGE ###
python main.py --help

##### QUICK START #####
The following is a quick-start guide to using the main script to run the
Dwell Time analysis.  Before starting, make sure you have the following information:

  * Your WATCHMAN detector's specifications.  Currently needed specifications
    for the code that generates an experiment's signal/background rates is:
    - Photocoverage
    - Buffer volume
    - PMT type (low_radioactivity or normal_radioactivity)
    - PMT orientation ("center_point" or "normal_point")
    - Are PMT shields used ("true" or "false")

1. Enter the ./DB/ directory and start a new JSON file with the same structure
   as the BoulbySignalBackground.json default.  
2. Enter the signal/background rates and WATCHMAN detector configuration
   as is done for entries in the BoulbySignalBackground.json default file.
3. Enter the lib/config/ directory and open DBConfig.py.  Configure the database
   reader to read from your JSON file and to look for the WATCHMAN detector
   configuration that you want to simulate.
4. in the lib/config/ directory, open schedule_config.py.  Configure the reactor
   operation schedule to your liking.  The methodology behind this config file
   is to specify the length of outages, spacing between outages, and when the
   first long outage occurs.  The structure of the operation schedule is formed
   automatically around these dimensions.  Default is the optimal Hartlepool
   operational structure based on past data.

5. Go to WATCHStat's home directory and run the following:
$ python main.py -d -j -10 --debug
   
   This will do several things:
   - Show various plots giving details on what your generated operation
     schedule looks like
   - Proceed to generate the simulated experiments and run the dwell time
     analysis on each experiment
   - Save the results of all 3-sigma observation days to the file
     jobresults/results_j10.json

6. Open python on the command line (I like to use ipython) and do:
$ import json
$ with open("./jobresults/results_j10.json","r") as f:
    thedata = json.load(f)

We have now loaded our results JSON as a python dictionary.  To plot the
cumulative distribution of the dwell time results, do:

$ import plot.CLGraph as clg
$ ourgrapher = clg.DwellTimeCL(thedata)

Upon generating the ourgrapher object, a plot of the cumulative distribution
should come up.  To see possible methods you can use to tweak the graph, do

$ ourgrapher. [HIT THE TAB BUTTON]

And to see what a method does, do
$ ourgrapher.amethod?

