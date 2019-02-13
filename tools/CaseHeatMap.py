#When run in a directory containing all timebin results (outputs from 
#main.py), produces a table showing the data cleaning sacrifice and
#Data/MC ratio for each timebin.  

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context('poster')
sns.set_style("darkgrid")
import os,sys,time
import glob
import json

basepath = os.path.dirname(__file__)
MAINDIR = os.path.abspath(basepath)

class CaseHeatMapMaker(object):
    def __init__(self, casetables_array=[]):
        self.case_table_dicts = casetables_array
        self.dataframe = None
        #Hard-coded to match requested table entries
        self.signal_values = ["Reactor","Accidentals","FastN"]
        self.case_table_keys = ["case","Photocoverage","buffer_size","Reactor","Accidentals","FastN","50CL","68CL","90CL","95CL"]

    def add_case(self,case_dict):
        self.case_table_dicts.append(case_dict)

    def load_dataframe(self):
        #First, initialize dataframe dict's different arrays
        dataframe_dict = {}
        for key in self.case_table_keys:
            dataframe_dict[key] = []
        for case in self.case_table_dicts:
            dataframe_dict = self.AddCaseValues(case, dataframe_dict)
        self.dataframe = pd.DataFrame(dataframe_dict)

    def AddCaseValues(self,casedict,dataframe_dict):
        '''Write a table line with the values in the given dictionary. Specific to output
        from WATCHStat right now'''
        configdict = casedict["WATCHMANConfiguration"]
        determdays = sorted(casedict["determination_days"],key=int)
        have_reac = False
        for val in self.case_table_keys:
            if val in configdict:
                dataframe_dict[val].append(configdict[val])
            elif val in self.signal_values:
                sigdict = configdict["Signal_Contributions"]
                for sigval in sigdict:
                    if (sigval=="Core_1" or sigval=="Core_2") and val == "Reactor" and not have_reac:
                        dataframe_dict[val].append(sigdict["Core_1"])
                        have_reac = True
                    elif val == sigval:
                        dataframe_dict[val].append(sigdict[sigval])
            elif val.find("CL") != -1:
                print("VAL IS " + str(val))
                clfrac = float(val.rstrip("CL"))/100.
                print("CLFRAC: " + str(clfrac))
                clval = determdays[int(float(len(determdays))*clfrac)]
                print("CLVAL IS: " + str(clval))
                dataframe_dict[val].append(clval)
        print("DATADICT IS : " + str(dataframe_dict))
        return dataframe_dict

    def MakeCLHeatMap(self,CL="90CL",normed=False):
        if CL not in self.dataframe:
            print("You must choose a set of CL values in the case table")
            return
        norm_max = float(max(self.dataframe[CL]))
        if normed == True:
            self.dataframe[CL] = self.dataframe[CL]/float(max(self.dataframe[CL]))
        pivoted_DF = self.dataframe.pivot("Photocoverage","buffer_size",CL)
        ax = sns.heatmap(pivoted_DF,annot=True)
        plt.ylabel("Photocoverage")
        plt.xlabel("buffer_size (m)")
        plt.title("Normalized comparison of dwell time analysis confirmation at 68%% CL \n" + \
                "Normalized to %f days"%(norm_max))
        plt.show()


def getAllJsons(direc):
    '''returns an array of dictionary objects from any json file in the given directory'''
    thejsons = []
    filearr = glob.glob("%s/*.json"%(direc))
    for f in filearr:
        with open(f,"r") as fi:
            thejsons.append(json.load(fi))
    return thejsons

if __name__=='__main__':
    jsons = getAllJsons(sys.argv[1])
    OurMaker = CaseHeatMapMaker(casetables_array=jsons)
    OurMaker.load_dataframe()
    OurMaker.MakeCLHeatMap(CL="68CL",normed=True)
