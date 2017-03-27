# Classes written read from the /DB/ directory and parse the JSON dictionaries
# into usable python objects.

import os, json
import sys

basepath = os.path.dirname(__file__)
dbpath = os.path.abspath(os.path.join(basepath, "..", "DB"))

BOULBY_SIGNALS = 'BoulbySignals.json'
BOULBY_SIGNALS_PC = 'BoulbySignals_PC.json'
FAIRPORT_SIGNALS_PC = "FairportSignals_PC.json"
#Class takes in an efficiency and holds the IBD events/day for all defined
#signal sources at Boulby for that efficiency
class Signals(object):
    def __init__(self, efficiency, site):
        self.efficiency = efficiency
        self.signals = 'none'
        self.site = site
        self.DBget()


    def DBget(self):
        if site == "Boulby":
            sigpath = os.path.abspath(os.path.join(dbpath, BOULBY_SIGNALS))
        if site == "Fairport":
            print("No implementation of Fairport site as a function of" + \
                    "efficiency. Exiting")
            sys.exit(0)
        with open(sigpath) as data_file:
            data = json.load(data_file)
            for case in data["Efficiency_Cases"]:
                if case["Detection_Efficiency"] == self.efficiency:
                    self.signals = case["Signal_Contributions"] 
            if self.signals == 'none':
                    print("Efficiency not found in database.  Check your" + \
                            "efficiency input.")
                    sys.exit(0)

    def show(self):
        if self.signals != 'none':
            for entry in self.signals:
                print(str(entry) + ":" + str(self.signals[entry]))

class Signals_PC(object):
    def __init__(self, pc, site):
        self.pc = pc
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
            for case in data["Photocoverage_Cases"]:
                if case["Photocoverage"] == self.pc:
                    self.signals = case["Signal_Contributions"] 
            if self.signals == 'none':
                    print("Photocoverage not found in database.  Check your" + \
                            "photocoverage input.")
                    sys.exit(0)

    def show(self):
        if self.signals != 'none':
            for entry in self.signals:
                print(str(entry) + ":" + str(self.signals[entry]))

