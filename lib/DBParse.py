# Classes written read from the /DB/ directory and parse the JSON dictionaries
# into usable python objects.

import os, json
import sys
import config.DBConfig as dbc

basepath = os.path.dirname(__file__)
dbpath = os.path.abspath(os.path.join(basepath, "..", "DB"))


class Signals_PC(object):
    def __init__(self, pc, pmttype, bufsize, site,orientation=None,has_shields=None):
        self.pc = pc
        self.bufsize = bufsize
        self.pmttype = pmttype
	self.orient = orientation
	self.has_shields = has_shields
        self.signals = 'none'
        self.site = site

    def set_site(self,site):
        '''set which site you want to load from the database JSON given'''
        self.site = site

    def set_orientation(self,orientation):
        '''set which PMT orientation S/B dict you want to load from the database JSON given'''
        self.orient = orientation

    def set_pmttype(self,pmttype):
        '''set which PMT type S/B dict you want to load from the database JSON given'''
        self.pmttype = pmttype
    
    def set_bufsize(self,bufsize):
        '''set which buffer size S/B dict you want to load from the database JSON given'''
        self.bufsize = bufsize

    def set_shields(self,has_shields):
        '''set if the S/B dict you want to load from the database JSON given has shields or not'''
        self.has_shields = has_shields

    def load_signal_dict(self):
        if self.site == "Boulby":
            sigpath = os.path.abspath(os.path.join(dbpath, dbc.BOULBY_SIGNALS_DBENTRY))
        if self.site == "Fairport":
            sigpath = os.path.abspath(os.path.join(dbpath, dbc.FAIRPORT_SIGNALS_DBENTRY))
        with open(sigpath) as data_file:
            data = json.load(data_file)
            for case in data["SB"]:
                if case["Photocoverage"] == self.pc and case["pmt_type"]==self.pmttype \
                        and case["buffersize"] == self.bufsize:
                    try:
                        if case["orientation"] == self.orient and case["has_shields"] == \
                                self.has_shields:
                            self.signals = case["Signal_Contributions"]
                            break
                    except KeyError:
                        print("orientation and shields specs not found in DB entry.")
                        print("Accepting first matching photocoverage, pmt_type, and bufsize")
                        self.signals = case["Signal_Contributions"]
                        break 
            if self.signals == 'none':
                    print("Given detector configuration not found in database.  Check your" + \
                            "photocoverage input.")
                    print("You must, at a minimum, specify: PMT type, buffer size, PMT photocoverage")
                    sys.exit(0)

    def show(self):
        if self.signals != 'none':
            for entry in self.signals:
                print(str(entry) + ":" + str(self.signals[entry]))

