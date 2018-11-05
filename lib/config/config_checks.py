#This should be run at start of main.  Will confirm that you have chosen
#A valid configuration to run the software.
import DBConfig as dbc

def runchecks():
    if dbc.PHOTOCOVERAGE is None:
        print("PLEASE SPECIFIY A PHOTOCOVERAGE IN THE CONFIG FILE IN lib/config/")
        sys.exit(0)
    if dbc.BUFFERSIZE is None:
        print("PLEASE SPECIFY A BUFFER SIZE IN THE CONFIG FILE IN lib/config/")
        sys.exit(0)
    if dbc.PMTTYPE is None:
        print("PLEASE SPECIFY A PMT TYPE IN THE CONFIG FILE IN lib/config/")
        sys.exit(0)

