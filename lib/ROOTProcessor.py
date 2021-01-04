import uproot
import numpy as np
import glob
import pandas as pd

def NtuplesToPD(directory,thetreename):
    '''
    Simple method that uses the ROOTProcessor to convert all *.ntuple.root files
    in a directory into a single Pandas DataFrame.

    inputs:
        directory [string]
        Path to the directory containing all ntuples of interest.

        thetreename [string]
        Name of the tree in the ROOT ntuples to process into the Pandas DataFrame.
    '''
    flist = glob.glob("%s/*.ntuple.root"%(directory))
    fproc = ROOTProcessor(treename=thetreename)
    for f in flist:
        fproc.addROOTFile(f)
    data = fproc.getProcessedData()
    df = pd.DataFrame(data)
    return df

class ROOTProcessor(object):
    '''
    Class which utilizes the uproot library to convert simple ROOT ntuple files
    to dictionaries, which readily convert to pandas DataFrames.

    TODOs:
      - Would be nice to use uproot in a way where the entire ROOT file isn't loaded
        into memory.  
    '''
    def __init__(self,treename="phaseII"):
        '''
        Initialization inputs:
            treename [string]
            Name of the tree in the ROOT ntuple to convert to a pandas
            dataframe.
        '''
        print("ROOTProcessor initializing")
        self.treename = treename
        self.processed_data = {}
        self.files_processed = []

    def getProcessedData(self):
        '''
        Returns a dictionary containing data from all ROOT ntuples that have been added
        to the ROOTProcessor class.
        '''
        if not self.processed_data:
            print("processed data array empty.  Did you process any data?")
        return self.processed_data

    def clearProcessedData(self):
        '''
        Empties the current processed_data dictionary.
        '''
        self.processed_data = {}
        self.files_processed = []

    def setTreeName(self,treename="phaseII"):
        '''
        Set the tree of data to be accessed from loaded ROOT files.

        Input:
            treename [string]
            Tree in ROOT datafiles to be loaded.
        '''
        self.treename = treename

    def addROOTFiles(self,rootfilelist,btg=None):
        for f in rootfilelist:
            self.addROOTFile(rootfile,branches_to_get=btg)

    def addROOTFile(self,rootfile,branches_to_get='all'):
        '''
        Opens the root ntuple file at the path given and append it's data
        to the current data dictionary.
        
        Input:
            rootfile [string]
            Path to rootfile to open.

            branches_to_get [array]
            Array of data variables to load into the dictionary.  Use to
            specify specific data types in ROOT file to collect.
        '''
        print("Processing rootfile %s"%(rootfile))
        f = uproot.open(rootfile)
        ftree = f.get(self.treename)
        all_data = ftree.keys()
        seen_data = []
        for dattype in all_data:
                if branches_to_get is not 'all':
                    #if dattype.decode('utf-8') not in branches_to_get: 
                    if dattype not in branches_to_get: 
                        continue
                if dattype not in seen_data: #Hack to ignore duplicate ntuple entries
                    seen_data.append(dattype)
                    thistype_processed = ftree.get(dattype).array()
                    self._appendProcessedEntry(dattype,thistype_processed)
        self.files_processed.append(rootfile) 

    def _appendProcessedEntry(self, dattype, thistype_processed):
        '''
        Appends processed data to the current processed_data dictionary.

        Inputs:
            dattype [string]
            key associated with the data location in self.processed_data.

            thistype_processed [array]
            numpy array of data pulled from a ROOT file using uproot.
        '''
        #dattype_key = dattype.decode('utf-8')
        dattype_key = dattype
        if dattype_key in self.processed_data:
            thistype_proclist = thistype_processed.tolist()
            self.processed_data[dattype_key] = self.processed_data[dattype_key] + \
                                           thistype_proclist
        else:
            self.processed_data[dattype_key] = []
            thistype_proclist = thistype_processed.tolist()
            self.processed_data[dattype_key] = self.processed_data[dattype_key] + \
                                           thistype_proclist
