########## SITE SELECTION AND WHAT CORES ARE KNOWN/UNKNOWN #############

##### Choose the WATCHMAN configuration (defines signal/background rates) #####
#### PHOTOCOVERAGE, BUFFERSIZE, AND PMTTYPE MUST HAVE A VALUE #################
#### PMT_ORIENTATION OR HAVING SHIELDS ARE OPTIONAL (set to None if want to ignore)##
SIGNALS_DBENTRY = 'BoulbySignalBackground.json' #'PMTOrientSB.json' #Choose the database of S/B rates

# DETECTOR SPECS YOU WANT (must match key/values of SIGNALS_DBENTRY entries)#
# If specifications is empty, the first entry in 
# BOULBY_SIGNALS_DBENTRY will be loaded

specifications = {}
specifications['site'] = "Boulby"  #Either Boulby or Fairport implemented
specifications['Photocoverage'] = 0.25
specifications['buffer_size'] = 1.5
specifications['pmt_type'] = 'low_activity'
#specifications['pmt_orientation'] = "default_point"
#specifications['has_shields'] = "true"

#PHOTOCOVERAGE = 0.25  #Choose the photocoverage you want from the database
#BUFFERSIZE = 1.5  #Choose your buffer size, in meters
#PMTTYPE = "low_activity" #regular_activity, low_activity, or 5050mix
#PMT_ORIENTATION = None #center_point, normal_point, or None to ignore
#HAS_SHIELDS = None             #true or false, or None to ignore


###########END CONFIGURING BASED ON OPTIONS ABOVE#####################

cores = {}
if specifications['site']=="Boulby":
    cores["core_names"] = ['Core_1','Core_2']  #Must match entries in DB used
    cores["known_cores"] = ['Core_1','Core_2'] #Tells analyses which cores are known
    cores["unknown_cores"] = []                #Tells the analyses which cores are unknown
if specifications['site']=="Fairport":
    cores["core_names"] = ["Core_1"]
    cores["known_cores"] = ["Core_1"]
    cores["unknown_cores"] = []

PBKG_DATA_TYPES = ["208Tl_LIQUID_CHAIN_232TH_NA","208Tl_PMT_CHAIN_232TH_NA"]
DBKG_DATA_TYPES = ["208Tl_LIQUID_CHAIN_232TH_NA","208Tl_PMT_CHAIN_232TH_NA"]
PSIG_DATA_TYPES = ["IBDPositron_LIQUID_ibd_p"]
DSIG_DATA_TYPES = ["IBDNeutron_LIQUID_ibd_n"]

BRANCHES = ['good_pos','distpmt','pe','n9']

