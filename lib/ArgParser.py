import optparse

#Here we have the argument parser inputs
#Isolated to keep the main script clean

parser = optparse.OptionParser()
parser.add_option("--debug",dest="debug",action="store_true",default="False")

#Options determine what signal/background rates to get from the database
parser.add_option('-c','--photocov',action="store",dest="pc", \
        type="float",default=None,help="Photocoverage of WATCHMAN " + \
        "you want the signal/background rates for (15pct, 20pct, or 25pct")
parser.add_option('-b','--buffersize',action="store",dest="bufsize", \
        type="float",default=1.5,help="Buffer size in meters you want "+\
        "the signal/background rates for (1.5, 2.0, or 2.5)")
parser.add_option('-a','--activity',action="store", dest="activity", \
        type="string",help="Specify what type of PMTs you want the signal"+\
        "/background rates for (normal_activity, 5050mix, or low_activity)")

#Options determine what experiments are ran with the given configuration
#Currently, running one at a time is suggested
parser.add_option('-d','--dwelltime',action="store_true",dest="dwelltime", \
        default="False",help="Search for difference in IBD numbers in known"+\
        "reactor on and reactor off data sets")
parser.add_option('-p','--poisfit',action="store_true",dest="posfit", \
        default="False",help="Fit a poisson to 'rector off' data for known reactors")
parser.add_option('-s','--SPRT',action="store_true",dest="sprt", \
        default="False",help="Run an SPRT over all on days for known reactors")
parser.add_option('-l','--Kalman',action="store_true",dest="kalman", \
        default="False",help="Run the Kalman Filter probability test on"+\
        "each statistical experiment generated")
parser.add_option('-f','--FB',action="store_true",dest="forwardbackward", \
        default="False",help="Train the judge with training schedule, then "+\
        "Run the Forward-Backward algorithm and judging on test schedule expts")
parser.add_option('-w','--Window',action="store_true",dest="window", \
        default="False",help="Run the moving window smoothing algorithm on"+\
        "each statistical experiment generated")

#Defines the job number appended to results JSON saved in output directory
parser.add_option('-j','--jobnum',action="store",dest="jobnum", \
        type="int",default=0,help="Job number (for saving data/grid use)")

(options,args) = parser.parse_args()
DEBUG = options.debug
SPRT = options.sprt
KALMAN = options.kalman
FORWARDBACKWARD = options.forwardbackward
WINDOW = options.window
POISFIT = options.posfit
DWELLTIME = options.dwelltime
jn = options.jobnum
PHOTOCOVERAGE = None
PMTTYPE = None
BUFFERSIZE = None
if options.pc is not None:
    PHOTOCOVERAGE = options.pc
if options.activity is not None:
    PMTTYPE = options.activity
if options.bufsize is not None:
    BUFFERSIZE = options.bufsize


