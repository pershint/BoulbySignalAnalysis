#Here we'll write a config file to read from, rather than all of the input
#optons that we are seeing right now.  It's getting too hectic in the main.
import config_checks as cc
from .. import DBParse as dp

########################BEGIN CONFIGURABLES#############################

########## SITE SELECTION AND WHAT CORES ARE KNOWN/UNKNOWN #############
SITE = "Boulby"  #Either Boulby or Fairport implemented

cores = {}
if SITE=="Boulby":
    cores["core_names"] = ['Core_1','Core_2']  #Must match entries in DB used
    cores["known_cores"] = ['Core_1','Core_2'] #Tells analyses which cores are known
    cores["unknown_cores"] = []                #Tells the analyses which cores are unknown
if SITE=="Fairport":
    cores["core_names"] = ["Core_1"]
    cores["known_cores"] = ["Core_1"]
    cores["unknown_cores"] = []


##### Choose the WATCHMAN configuration (defines signal/background rates) #####
PHOTOCOVERAGE = 0.25  #Choose the photocoverage you want from the database
BUFFERSIZE = 1.5  #Choose your buffer size, in meters
PMTTYPE = "low_activity" #regular_activity, low_activity, or 5050mix

####### NUMBER OF EXPERIMENTS TO GENERATE FOR THE ANALYSIS RUN ########
NEXPERIMENTS = 100 #Number of experiments generated in analysis run (# Test 
                    #expts. for the FB algorithm
NTRAININGEXPTS = 100 #Number of experiments to test the FB algorithm's Judge with
RESOLUTION = 1 #Exp_Generator does re-binning of data by request; this gives
               #The bin resolution in days

######SCHEDULE FOR TRAINING DATA USED IN ANALYSES#######
###### Also acts as the training schedule for FB algorithm running ########
schedule_dict = {}
schedule_dict["OFF_TIME"] = 60    #Days that cores turn off for a long outage
schedule_dict["UP_TIME"] = 1035   #Day interval between long outages
schedule_dict["KILL_CORES"] = []#"Core_2"] #List the name of core(s) to shut down
schedule_dict["KILL_DAYS"] = []#700] #List the days where cores in KILL_CORES shuts down
schedule_dict["TOTAL_RUN"] = 1550  #Total length of experiment
schedule_dict["MAINTENANCE_TIME"] =10 
schedule_dict["MAINTENANCE_INTERVAL"] = 106 #Day interval between maintenance outages

schedule_dict["FIRST_SHUTDOWNS"] = [1,549] #Match index with cores in "core_names"
schedule_dict["CORETYPES"] = cores

#######SCHEDULE FOR DATA USED TO TEST ANALYSES########
schedule_dict_test = {}
schedule_dict_test["OFF_TIME"] = 60    #Days that cores turn off for a long outage
schedule_dict_test["UP_TIME"] = 1035   #Day interval between long outages
schedule_dict_test["KILL_CORES"] = []#"Core_2"] #List the name of core(s) to shut down
schedule_dict_test["KILL_DAYS"] = [] #List the days where cores in KILL_CORES shuts down
schedule_dict_test["TOTAL_RUN"] = 1550  #Total length of experiment
schedule_dict_test["MAINTENANCE_TIME"] =10 
schedule_dict_test["MAINTENANCE_INTERVAL"] = 106 #Day interval between maintenance outages

schedule_dict_test["FIRST_SHUTDOWNS"] = [1,549] #Match index with cores in "core_names"
schedule_dict_test["CORETYPES"] = cores

####################END CONFIGURABLES##################################

###################BEGIN CONFIGURING BASED ON OPTIONS ABOVE############
signals={}
signals = dp.Signals_PC(PHOTOCOVERAGE,PMTTYPE,BUFFERSIZE, SITE)

###########END CONFIGURING BASED ON OPTIONS ABOVE#####################

##########RUN CHECKS FOR SENSIBLE CONFIGURATION#######################
cc.runchecks()

