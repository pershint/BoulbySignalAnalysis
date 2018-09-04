#Here we'll write a config file to read from, rather than all of the input
#optons that we are seeing right now.  It's getting too hectic in the main.
import config_checks as cc
from .. import DBParse as dp

########################BEGIN CONFIGURABLES#############################
SITE = "Boulby"  #Either Boulby or Fairport implemented

##### Choose either a photoverage or an efficiency, not both #####
PHOTOCOVERAGE = 0.25  #Choose the photocoverage you want from the database
BUFFERSIZE = 1.5  #Choose your buffer size, in meters
PMTTYPE = "low_activity" #regular_activity, low_activity, or 5050mix
NEXPERIMENTS = 10 #Number of experiments generated in analysis run
RESOLUTION = 1 #Exp_Generator does re-binning of data by request; this gives
               #The bin resolution in days

schedule_dict = {}
schedule_dict["OFF_TIME"] = 60    #Days that cores turn off for a long outage
schedule_dict["UP_TIME"] = 1035   #Day interval between long outages
schedule_dict["KILL_CORES"] = []#"Core_2"] #List the name of core(s) to shut down
schedule_dict["KILL_DAYS"] = []#700] #List the days where cores in KILL_CORES shuts down
schedule_dict["TOTAL_RUN"] = 1550  #Total length of experiment
schedule_dict["MAINTENANCE_TIME"] = 10
schedule_dict["MAINTENANCE_INTERVAL"] = 106 #Day interval between maintenance outages

schedule_dict["FIRST_KNOWNSHUTDOWNS"] = [1,549]
schedule_dict["FIRST_UNKNOWNSHUTDOWNS"] = []

#NOTE: These are not implemented for any use yet
schedule_dict["UNDECLARED_OUTAGE_CORE"] = "Core_1"
schedule_dict["UNDECLARED_OUTAGE_STARTS"] = [] #108]
schedule_dict["UNDECLARED_OUTAGE_LENGTHS"] = [30]

####################END CONFIGURABLES##################################

###################BEGIN CONFIGURING BASED ON OPTIONS ABOVE############
signals={}
signals = dp.Signals_PC(PHOTOCOVERAGE,PMTTYPE,BUFFERSIZE, SITE)

cores = {}
if SITE=="Boulby":
    cores["known_cores"] = ['Core_1','Core_2']  #Must match entries in DB used
    cores["unknown_cores"] = []
if SITE=="Fairport":
    cores["known_cores"] = ["Core_1"]
    cores["unknown_cores"] = []

###########END CONFIGURING BASED ON OPTIONS ABOVE#####################

schedule_dict["CORETYPES"] = cores
##########RUN CHECKS FOR SENSIBLE CONFIGURATION#######################
cc.runchecks()

