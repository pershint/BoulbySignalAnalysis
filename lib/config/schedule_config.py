#Here we'll write a config file to read from, rather than all of the input
#optons that we are seeing right now.  It's getting too hectic in the main.
from .. import DBParse as dp
import db_config as dbc
########################BEGIN CONFIGURABLES#############################

###################BEGIN CONFIGURING BASED ON OPTIONS ABOVE############

####### NUMBER OF EXPERIMENTS TO GENERATE FOR THE ANALYSIS RUN ########
NEXPERIMENTS = 10 #Number of experiments generated in analysis run (# Test 
                    #expts. for the FB algorithm
NTRAININGEXPTS = 10 #Number of experiments to test the FB algorithm's Judge with
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
schedule_dict["CORETYPES"] = dbc.cores

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
schedule_dict_test["CORETYPES"] = dbc.cores

####################END CONFIGURABLES##################################

