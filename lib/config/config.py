#Here we'll write a config file to read from, rather than all of the input
#optons that we are seeing right now.  It's getting too hectic in the main.
import config_checks as cc
from .. import DBParse as dp

########################BEGIN CONFIGURABLES#############################
SITE = "Boulby"  #Either Boulby or Fairport implemented

##### Choose either a photoverage or an efficiency, not both #####
PHOTOCOVERAGE = 0.25  #Choose the photocoverage you want from the database
DETECTION_EFF = None #Detection efficiency for IBDs

RESOLUTION = 1 #Exp_Generator does re-binning of data by request; this gives
               #The bin resolution in days

schedule_dict = {}
schedule_dict["OFF_TIME"] = 60
schedule_dict["UP_TIME"] = 1035
schedule_dict["KILL_CORES"] = ['Core_2']
schedule_dict["KILL_DAYS"] = [700]
schedule_dict["TOTAL_RUN"] = 2000
schedule_dict["MAINTENANCE_INTERVAL"] = 106#None
schedule_dict["MAINTENANCE_TIME"] = 10

schedule_dict["FIRST_KNOWNSHUTDOWNS"] = [1]
schedule_dict["FIRST_UNKNOWNSHUTDOWNS"] = [549]

#NOTE: These are not implemented for any use yet
schedule_dict["UNDECLARED_OUTAGE_CORE"] = "Core_1"
schedule_dict["UNDECLARED_OUTAGE_STARTS"] = [] #108]
schedule_dict["UNDECLARED_OUTAGE_LENGTHS"] = [30]

####################END CONFIGURABLES##################################

###################BEGIN CONFIGURING BASED ON OPTIONS ABOVE############
signals={}
if PHOTOCOVERAGE is not None:
    signals = dp.Signals_PC(PHOTOCOVERAGE, SITE)
elif DETECTION_EFF is not None:
    signals = dp.Signals(DETECTION_EFF, SITE)

cores = {}
if SITE=="Boulby":
    cores["known_cores"] = ['Core_1']  #Must match entries in DB used
    cores["unknown_cores"] = ['Core_2']
if SITE=="Fairport":
    cores["known_cores"] = ["Core_1"]
    cores["unknown_cores"] = []

###########END CONFIGURING BASED ON OPTIONS ABOVE#####################

schedule_dict["CORETYPES"] = cores
##########RUN CHECKS FOR SENSIBLE CONFIGURATION#######################
cc.runchecks()

