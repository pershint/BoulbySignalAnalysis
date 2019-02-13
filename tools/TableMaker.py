#When run in a directory containing all timebin results (outputs from 
#main.py), produces a table showing the data cleaning sacrifice and
#Data/MC ratio for each timebin.  

import numpy as np
import os,sys,time
import glob
import json

basepath = os.path.dirname(__file__)
MAINDIR = os.path.abspath(basepath)

class LaTeXTable(object):
    def __init__(self):
        self.tlines = []
        self.title_keys = []


    def SetTitleKeys(self,key_array):
        '''Set the array of title names; will also be used to search dictionaries for values 
        to append to table'''
        self.title_keys = key_array

    def ClearTable(self):
        self.tlines = []

    def LoadTable(self,fname):
        '''Takes in a filename and loads the file into the table lines'''
        table = None
        with open(fname,"r") as f:
            table = f.readlines()
        self.tlines = table
        print(self.tlines)

    def AddTableLine(self,line):
        self.tlines.append(line)

    def SetTableLine(self,linenum,line):
        self.tlines[0] = line

    def AddCommentLine(self,string):
        self.tlines.append("%% %s \n"%(string))

    def SaveTable(self,name):
        f = open(name,'w')
        for line in self.tlines:
            f.write(line)
        f.close()

    def MakeTitle(self):
        if not self.title_keys:
            print("You need an array of titles, which will find the right values from loaded dicts.")
            return
        thetitle = ""
        for key in self.title_keys:
            thetitle += "%s & "%(key)
        thetitle = thetitle.rstrip(" & ")
        thetitle += "\\\\ \n"
        if not self.tlines:
            self.tlines.append(thetitle)
        else:
            self.tlines[0] = thetitle


class CaseTable(LaTeXTable):
    def WriteTableLine(self,casedict):
        '''Write a table line with the values in the given dictionary. Specific to output
        from WATCHStat right now'''
        theline = ""
        values_to_write = []
        signal_values = ["Reactor","Accidentals","FastN"]
        configdict = casedict["WATCHMANConfiguration"]
        determdays = sorted(casedict["determination_days"],key=int)
        for val in self.title_keys:
            if val in configdict:
                values_to_write.append(configdict[val])
            elif val in signal_values:
                sigdict = configdict["Signal_Contributions"]
                for sigval in sigdict:
                    if (sigval=="Core_1" or sigval=="Core_2") and val == "Reactor":
                        values_to_write.append(sigdict["Core_1"])
                    elif val == sigval:
                        values_to_write.append(sigdict[sigval])
            elif val.find("CL") != -1:
                print("VAL IS " + str(val))
                clfrac = float(val.rstrip("CL"))/100.
                print("CLFRAC: " + str(clfrac))
                clval = determdays[int(float(len(determdays))*clfrac)]
                print("CLVAL IS: " + str(clval))
                values_to_write.append(clval)

        for entry in values_to_write:
            theline += "%s & "%(entry)
        theline = theline.rstrip(" & ")
        theline+="\\\\ \n"
        self.tlines.append(theline)

    def SortLines(self):
        '''Sorts lines by their first index'''
        linenumbers = []
        print("TLINES: " + str(self.tlines[1:len(self.tlines)]))
        for j,line in enumerate(self.tlines):
            if j == 0:
                continue
            line = line.split(" & ")
            linenumbers.append(int(line[0]))
        #sort and get array indices
        print("LINE NUMBERS: " + str(linenumbers))
        sorted_lines = [x for _,x in sorted(zip(linenumbers,self.tlines[1:len(self.tlines)]))]
        self.tlines[1:len(self.tlines)] = sorted_lines

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
    caseTable = CaseTable()
    caseTable.SetTitleKeys(["case","Photocoverage","buffer_size","Reactor","Accidentals","FastN","50CL","68CL","90CL","95CL"])
    caseTable.MakeTitle()
    for case in jsons:
        caseTable.WriteTableLine(case)
    caseTable.SortLines()
    caseTable.SaveTable("test.txt")
