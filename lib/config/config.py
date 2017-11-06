#Here we'll write a config file to read from, rather than all of the input
#optons that we are seeing right now.  It's getting too hectic in the main.
import config_checks as cc
from .. import DBParse as dp

########################BEGIN CONFIGURABLES#############################
SITE = "Boulby"  #Either Boulby or Fairport implemented

##### Choose either a photoverage or an efficiency, not both #####
PHOTOCOVERAGE = 0.25  #Choose the photocoverage you want from the database
DETECTION_EFF = None #Detection efficiency for IBDs

RESOLUTION = 7 #Exp_Generator does re-binning of data by request; this gives
               #The bin resolution in days

maintenance_interval = None #Time interval between large outages
maintenance_length = None #Time for which a reactor is off for maintenance

schedule_dict = {}
schedule_dict["OFF_TIME"] = 60
schedule_dict["UP_TIME"] = 1080
schedule_dict["KILL_DAY"] = None
schedule_dict["TOTAL_RUN"] = 1800
schedule_dict["MAINTENANCE_INTERVAL"] = None
schedule_dict["MAINTENANCE_TIME"] = 10

schedule_dict["FIRST_KNOWNSHUTDOWNS"] = [1, 549]
schedule_dict["FIRST_UNKNOWNSHUTDOWNS"] = []
schedule_dict["UNDECLARED_OUTAGE_STARTS"] = [108]
schedule_dict["UNDECLARED_OUTAGE_CORE"] = "Core_1"
schedule_dict["UNDECLARED_OUTAGE_LENGTH"] = [30]

####################END CONFIGURABLES##################################

###################BEGIN CONFIGURING BASED ON OPTIONS ABOVE############
signals={}
if PHOTOCOVERAGE is not None:
    signals = dp.Signals_PC(PHOTOCOVERAGE, SITE)
elif DETECTION_EFF is not None:
    signals = dp.Signals(DETECTION_EFF, SITE)

cores = {}
if SITE=="Boulby":
    cores["known_cores"] = ['Core_1','Core_2']  #Must match entries in DB used
    cores["unknown_cores"] = []
if SITE=="Fairport":
    cores["known_cores"] = ["Core_1"]
    cores["unknown_cores"] = []

###########END CONFIGURING BASED ON OPTIONS ABOVE#####################

##########RUN CHECKS FOR SENSIBLE CONFIGURATION#######################
cc.runchecks()

