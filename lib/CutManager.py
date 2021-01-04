import numpy as np
import pandas as pd

class CutManager:
    def __init__(self, df = None):
        self.df = df
        self.resetind = True 
        self.cuts = []

    def SetResetIndices(self, ri):
        '''
        Set whether or not to reset index values after applying cuts.

        Input:
            ri [bool]
            Boolean of true or false for whether to reset indices.
        '''
        self.resetind = ri

    def LoadDataFrame(self, df):
        '''
        Loads a new dataframe into the CutManager class.  Cuts that have been
        applied so far are reset.

        Input:
            df [pandas.DataFrame]
        '''
        self.df = df
        self.cuts = []

    def ApplyCutValue(self,variable,cut,condition):
        '''
        Applies a cut on a single variable to the currently loaded dataframe.

        Inputs:
            variable [string]
            String that corresponds to a single variable in the pandas dataframe.

            cut [float]
            Cut value to be placed on the input variable.

            condition [string]
            Specifies what range of values are accepted.  Accepted inputs:
            "lt" (less than), "gt" (greater than), 
            "lte" (less than-equal to), "gte" (greater than-equal to).
        '''
        if condition=="lt":
            self.df = self.df.loc[self.df[variable]<cut].reset_index(drop=self.resetind)
        elif condition=="lte":
            self.df = self.df.loc[self.df[variable]<=cut].reset_index(drop=self.resetind)
        elif condition=="gt":
            self.df = self.df.loc[self.df[variable]>cut].reset_index(drop=self.resetind)
        elif condition=="gte":
            self.df = self.df.loc[self.df[variable]>=cut].reset_index(drop=self.resetind)
        else:
            print("Inputs not recognized!  Not applying cuts.")
            print("Inputs were: %s %f %s"%(variable,cut,condition))
            return
        self.cuts.append("%s %f %s"%(variable,cut,condition))
        return

    def ApplyCutLabel(self,variable,label,ar):
        '''
        Applies a cut on a single variable to the currently loaded dataframe.

        Inputs:
            variable [string]
            String that corresponds to a single variable in the pandas dataframe.

            label [string]
            Label to search for in variable column of dataframe.

            ar [string]
            Either "accept" or "reject", to specify whether or not to remove the label
            or keep only the label.
        '''
        if ar=="accept":
            self.df = self.df.loc[self.df[variable]==label].reset_index(drop=self.resetind)
        if ar=="accept":
            self.df = self.df.loc[self.df[variable]!=label].reset_index(drop=self.resetind)
        else:
            print("Inputs not recognized!  Not applying cuts.")
            print("Inputs were: %s %f %s"%(variable,label,ar))
            return
        self.cuts.append("%s %f %s"%(variable,label,ar))
        return

    def GetDataFrameWithCuts(self):
        return self.df

    def GetListOfCurrentCuts(self):
        return self.cuts

    def WriteCutsToFile(self,filepath):
        with open(filepath,"a") as f:
            for cut in self.cuts:
                f.write(cut)
            f.close()
