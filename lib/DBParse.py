# Classes written read from the /DB/ directory and parse the JSON dictionaries
# into usable python objects.

import os, json
import sys

basepath = os.path.dirname(__file__)
dbpath = os.path.abspath(os.path.join(basepath, "..", "DB"))

BOULBY_SIGNALS_PC = 'BoulbySignalBackground.json'
FAIRPORT_SIGNALS_PC = "FairportSignals_PC.json"

class Signals_PC(object):
    def __init__(self, pc, pmttype, bufsize, site):
        self.pc = pc
        self.bufsize = bufsize
        self.pmttype = pmttype 
        self.signals = 'none'
        self.site = site
        self.DBget()


    def DBget(self):
        if self.site == "Boulby":
            sigpath = os.path.abspath(os.path.join(dbpath, BOULBY_SIGNALS_PC))
        if self.site == "Fairport":
            sigpath = os.path.abspath(os.path.join(dbpath, FAIRPORT_SIGNALS_PC))
        with open(sigpath) as data_file:
            data = json.load(data_file)
            for case in data["SB"]:
                if case["Photocoverage"] == self.pc and case["pmt_type"]==self.pmttype \
                        and case["buffersize"] == self.bufsize:
                    self.signals = case["Signal_Contributions"] 
            if self.signals == 'none':
                    print("Photocoverage not found in database.  Check your" + \
                            "photocoverage input.")
                    sys.exit(0)

    def show(self):
        if self.signals != 'none':
            for entry in self.signals:
                print(str(entry) + ":" + str(self.signals[entry]))

