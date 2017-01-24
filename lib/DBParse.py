# Classes written read from the /DB/ directory and parse the JSON dictionaries
# into usable python objects.

import os, json

basepath = os.path.dirname(__file__)
dbpath = os.path.abspath(os.path.join(basepath, "..", "DB"))

BOULBY_SIGNALS = 'BoulbySignals.json'

#Class takes in an efficiency and holds the IBD events/day for all defined
#signal sources at Boulby for that efficiency
class BoulbySignals(object):
    def __init__(self, efficiency):
        self.efficiency = efficiency
        self.signals = 'none'
        self.DBget()


    def DBget(self):
        boulbypath = os.path.abspath(os.path.join(dbpath, BOULBY_SIGNALS))
        with open(boulbypath) as data_file:
            data = json.load(data_file)
            for case in data["Efficiency_Cases"]:
                if case["Detection_Efficiency"] == self.efficiency:
                    self.signals = case["Signal_Contributions"] 
            if self.signals == 'none':
                    print("Efficiency not found in database.  Check your" + \
                            "efficiency input.")
    def show(self):
        if self.signals != 'none':
            for entry in self.signals:
                print(str(entry) + ":" + str(self.signals[entry]))

