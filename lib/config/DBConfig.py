########## SITE SELECTION AND WHAT CORES ARE KNOWN/UNKNOWN #############
SITE = "Boulby"  #Either Boulby or Fairport implemented

##### Choose the WATCHMAN configuration (defines signal/background rates) #####
#### PHOTOCOVERAGE, BUFFERSIZE, AND PMTTYPE MUST HAVE A VALUE #################
#### PMT_ORIENTATION OR HAVING SHIELDS ARE OPTIONAL (set to None if want to ignore)##
BOULBY_SIGNALS_DBENTRY = 'PMTOrientSB.json' #Choose the database of S/B rates
FAIRPORT_SIGNALS_DBENTRY = "FairportSignals_PC.json"
PHOTOCOVERAGE = 0.25  #Choose the photocoverage you want from the database
BUFFERSIZE = 1.5  #Choose your buffer size, in meters
PMTTYPE = "low_activity" #regular_activity, low_activity, or 5050mix
PMT_ORIENTATION = "normal_point" #center_point or normal_point
HAS_SHIELDS = "true"             #true or false


###########END CONFIGURING BASED ON OPTIONS ABOVE#####################

cores = {}
if SITE=="Boulby":
    cores["core_names"] = ['Core_1','Core_2']  #Must match entries in DB used
    cores["known_cores"] = ['Core_1','Core_2'] #Tells analyses which cores are known
    cores["unknown_cores"] = []                #Tells the analyses which cores are unknown
if SITE=="Fairport":
    cores["core_names"] = ["Core_1"]
    cores["known_cores"] = ["Core_1"]
    cores["unknown_cores"] = []



