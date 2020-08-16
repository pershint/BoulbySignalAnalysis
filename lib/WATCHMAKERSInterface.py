import os
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
        self.bonsaidir = None
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
        self.bonsaidir = self._BonsaiDirectory()
        self.data_types = self._GetAvailableDataTypes()

    def _BonsaiDirectory(self):
        '''
        Given the specified WATCHMAKERS directory, get the path to the 
        bonsai directory.
        '''
        bonsai_glob = glob.glob("%s/bonsai_root_files*"%(self.wmpath))
        print("BONSAI DIR GLOB: " + str(bonsai_glob))
        if len(bonsai_glob)<1:
            print("ERROR: No bonsai_root_files directory in WATCHMAKERS path!")
            return None
        if len(bonsai_glob)>1:
            print(("WARNING: Multiple bonsai_root_files directories in" + 
                " WATCHMAKERS directory!  Taking first found..."))
        return bonsai_glob[0]

    def _GetAvailableDataTypes(self):
        data_glob = glob.glob("%s/*/"%(self.bonsaidir))
        print("DATA DIRECTORY GLOB: " + str(data_glob)) 
        if len(data_glob)<1:
            print("ERROR: No ROOT data found in bonsai_root_files directory!")
            return None
        data_types = []
        for dtype in data_glob:
            thetype = dtype.replace(self.bonsaidir+"/Watchman_","").rstrip("/")
            data_types.append(thetype)
        return data_types

    def ListMergedBonsaiFiles(self):
        '''
        Method shows what merged files are available in the bonsai directory.
        '''
        mfiles = glob.glob("%s/merged_Watchman_*.root"%(self.bonsaidir))
        return mfiles

    def GetAllBonsaiFilesOfType(self,DataType):
        '''
        Method returns a list of all bonsai files for a single type of data.  

        Inputs:
            DataType [string]
            Name of the data directory to be viewed in the bonsai_root_files directory.  
            Do not give the full file path. 
        '''
        dfiles = glob.glob("%s/%s/*.root"%(self.bonsaidir,DataType))
        if len(dfiles)==0:
            print("No ROOT files found in bonsai directory %s/%s"%(self.bonsaidir,DataType))
        return dfiles

    def OpenMergedData(self,DataType):
        '''
        Opens a single merged file  

        Inputs:
            DataType [string]
            Name of the data type to be viewed.  Select an entry from self.data_types.  
            Do not give the full file path. 
        '''
        if os.path.exists("%s/merged_Watchman_%s.root"%(self.bonsaidir,DataType)):
            return uproot.open("%s/merged_Watchman_%s.root"%(self.bonsaidir,DataType))
        else:
            print("No merged file at %s/merged_Watchman_%s.root!"%(self.bonsaidir,DataType))
            return
