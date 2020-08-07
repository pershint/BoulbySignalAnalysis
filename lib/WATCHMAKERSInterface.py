import uproot
import numpy as np
import glob

###
# This class is designed to act as a python interface with any WATCHMAKERS
# output directory.  Specifically, this class provides an API for browsing
# the WATCHMAKERS bonsai files and reading in ROOT files using the uproot
# package.

# TODOs:
# Need to write the uproot part.  Start by writing a function that returns 
# an uproot object that can access all of the files in a single background
# source.

class WATCHMAKERSLoader(object):
    '''
    Class that is used to load in data from a WATCHMAKERS directory's
    bonsai files.
    Inputs:
        wmoutpath (string)
        Full path to the WATCHMAKERS directory.
    '''

    def __init__(self, wmoutpath):
        self.wmpath = None
        self._bonsaidir = None
        self._datadirs = None
        self.datadict = None
        self.SetWATCHMAKERSPath(wmoutpath)


    def GetAllDataTypes(self):
        '''
        Returns a list of all data types available in the current 
        WATCHMAKERS bonsai directory.
        '''
        return list(self.datadict.keys())

    def SetWATCHMAKERSPath(self,wmoutpath):
        '''
        Set the path to the WATCHMAKERS directory to analyze.  Will 
        also update the self.datadict dictionary to reflect all 
        bonsai files in the new WATCHMAKERS directory selected.
        '''
        if wmoutpath == self.wmpath:
            print("Input was same as current WATCHMAKERS path.")
            return
        if not os.path.isdir(wmoutpath):
            print("Input path to directory does not exist!")
            return
        self.wmpath = wmoutpath
        self._bonsaidir = self._BonsaiDirectory()
        self._datadirs = self.DataPaths()
        self.datadict = self._MakeDataDict()

    def _BonsaiDirectory(self):
        '''
        Given the specified WATCHMAKERS directory, get the path to the 
        bonsai directory.
        '''
        bonsai_glob = glob.glob("%s/bonsai_root_files*"%(self._wmpath))
        if len(bonsai_dirs)<1:
            print("ERROR: No bonsai_root_files directory in WATCHMAKERS path!")
            return None
        if len(bonsai_dirs)>1:
            print(("WARNING: Multiple bonsai_root_files directories in" + 
                " WATCHMAKERS directory!  Taking first found..."))
        return bonsai_glob[0]

    def _DataPaths(self):
        data_glob = glob.glob("%s/*/"%(self._bonsaidir))
        if len(data_glob)<1:
            print("ERROR: No ROOT data found in bonsai_root_files directory!")
            return None
        return data_glob

    def _MakeDataDict(self):
        '''
        Method looks in each data path, and produces a dictionary with the key
        being the data's name and the value being the list of ROOT files.
        '''
        ddict = {}
        for datadir in self._datadirs:
            data_type = datadir.lstrip(self._bonsaidir).rstrip("\n")
            rootfiles = glob.glob("%s/%.root"%(datadir))
            ddict[data_type] = rootfiles
        return ddict
