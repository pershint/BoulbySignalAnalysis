#This class takes a bunch of results from the Analysis2 class and combines
#Them based on if they have the same parameters or not.

import json
import glob

class dataFuser(object):
    def __init__(self):
        self.site = None
        self.determination_days = []
        self.no3sigmadays = 0
        self.num3siginarow = None
        self.pc = None
        self.schedule_dict = None
        self.details_inited = False

    def initDetails(self,seed):
        '''
        Fills in the descriptors used to make sure all metadata matches
        before fusing determination day datasets.
        '''
        self.site = seed["Site"]
        self.pc = seed["pc"]
        self.num3siginarow = seed["num3siginarow"]
        self.bufsize = seed["buffersize"]
        self.pmttype = seed["pmt_type"]
        self.schedule_dict = seed["schedule_dict"]
        self.details_inited = True

    def clearFuser(self):
        '''
        Clears all details, determination days, and no3sigma days
        Currently being combined.
        '''
        self.site = None
        self.determination_days = []
        self.no3sigmadays = 0
        self.num3siginarow = None
        self.pc = None
        self.bufsize = None
        self.pmttype = None
        self.schedule_dict = None
        self.details_inited = False

    def hassamemeta(self, data):
        '''
        Checks if the given data dictionary has the same metadata as
        Has been initialized using the initDetails function.
        '''
        if self.details_inited is False:
            print("There's no meta data currently loaded.")
            return False
        if self.site != data["Site"] or self.pmttype!=data["pmt_type"]:
            return False
        elif self.pc != data["pc"] or self.bufsize!=data["buffersize"]:
            return False
        elif self.schedule_dict != data["schedule_dict"]:
            return False
        else:
            return True

    def getResultsFromDir(self, loc):
        '''
        Takes in a directory name and gets the results from that directory.
        For each file, if the metadata matches, the data is added to the
        determination_days and no3sigma days held in the class.
        '''
        try:
            files = glob.glob(loc + "/results_j*.json")
        except:
            print("Error getting filenames from input directory.  Check" + \
                    "your specified directory and try again.")
            return
        for fname in files:
#            try:
                with open(fname,"r") as f:
                    data = json.load(f)
                    #Check if the metadata matches
                    if self.hassamemeta(data) is False:
                        self.initDetails(data)
                    elif self.hassamemeta(data):
                        self.determination_days.extend(data["determination_days"])
                        self.no3sigmadays += data["no3sigmadays"]
                    elif self.hassamemeta(data) is False and self.details_inited is True:
                        print("TRIED TO LOAD DATA WITH DIFFERENT META INFO...")
#            except:
#                print("Error loading in file" + str(fname) + ". Continuing")
#                continue

    def saveData(self, title):
        '''
        Saves the data combined thus far and the metadata that was confirmed
        to be the same for all of the days added.
        '''
        comb_dict = {}
        comb_dict["Site"] = self.site
        comb_dict["determination_days"] = self.determination_days
        comb_dict["no3sigmadays"] = self.no3sigmadays
        comb_dict["num3siginarow"] = self.num3siginarow
        comb_dict["pc"] = self.pc
        comb_dict["pmt_type"] = self.pmttype
        comb_dict["buffersize"] = self.bufsize
        comb_dict["schedule_dict"] = self.schedule_dict
        with open(title, "w") as f:
            json.dump(comb_dict, f, sort_keys=True, indent=4)
