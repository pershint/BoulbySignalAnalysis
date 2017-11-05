#This should be run at start of main.  Will confirm that you have chosen
#A valid configuration to run the software.
import config as c

def runchecks():
    if c.PHOTOCOVERAGE is not None and c.DETECTION_EFF is not None:
        print("CHOOSE EITHER A PHOTOCOVERAGE OR EFFICIENCY, NOT BOTH.")
        sys.exit(0)
    elif c.DETECTION_EFF is None and c.PHOTOCOVERAGE is None:
        print("CHOOSE A PHOTOCOVERAGE OR EFFICIENCY YO")
        sys.exit(0)


