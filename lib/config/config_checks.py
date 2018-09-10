#This should be run at start of main.  Will confirm that you have chosen
#A valid configuration to run the software.
import config_traindata as ctr
import config_traindata as ctt
def runchecks():
    if ctr.PHOTOCOVERAGE is None or ctt.PHOTOCOVERAGE is None:
        print("PLEASE SPECIFIY A PHOTOCOVERAGE IN THE CONFIG FILE IN lib/config/")
        sys.exit(0)
    if ctr.BUFFERSIZE is None or ctt.BUFFERSIZE is None:
        print("PLEASE SPECIFY A BUFFER SIZE IN THE CONFIG FILE IN lib/config/")
        sys.exit(0)
    if ctr.PMTTYPE is None or ctt.PMTTYPE is None:
        print("PLEASE SPECIFY A PMT TYPE IN THE CONFIG FILE IN lib/config/")
        sys.exit(0)

