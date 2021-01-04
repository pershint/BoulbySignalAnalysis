#!/usr/bin/python

#Main script for outputting reactor sensitivity study at Boulby in WATCHMAN
import json
import os.path
import sys
#import lib.TheJudge as tj
#import lib.DBParse as dp
#import lib.playDarts as pd
#import lib.Exp_Generator as eg
#import lib.Analysis as a

import lib.ArgParser as ap
import lib.WATCHMAKERSInterface as wmi
import lib.SimpleKDE as ske
import lib.CutManager as cm
import lib.LikelihoodCalculator as lc

from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context('poster')


basepath = os.path.dirname(__file__)
savepath = os.path.abspath(os.path.join(basepath,"jobresults"))

DEBUG = ap.DEBUG
DWELLTIME = ap.DWELLTIME
jn = ap.jn
TRAINING_LENGTH = 10000
TEST_LENGTH = 10000


#LOAD CONFIGURATIONS FOR DETECTOR, SIGNAL/BACKGROUND, AND REACTOR SCHEDULE
import config.schedule_config as sc
import config.db_config as dbc

if DEBUG is True:
    import graph.Histogram as h
    import graph.Exp_Graph as gr
    import matplotlib.pyplot as plt

cfg = None
with open("./config/WATCHStat_default.json") as f:
    cfg = json.load(f)


if __name__=='__main__':

    #  NEW DB configurables:
    #  - List of what branches to include in the analysis (position, n9, etc.)
    #  - Rates for EACH background type, as well as the signal
    #  - We'll probably need delayed and prompt PDFs for "S" and "B".
    #SO, what's our order of doing stuff in here now:
    #
    #  - First, use the WATCHMAKERSInterface to load the signal 
    #    and background ntuples as pandas dataframes. DONE
    #  - Split data into like 70/30 or something.  #TODO
    #    The 70 will somehow also be used to train the Judge as well.
    #  - Use the 70 to fill
    #    the LikelihoodCalculator with 1D KDEs from the ntuples. GETTING THERE
    #  - Given the input rates now, go modify the ExperimentGenerator class
    #    as I talked about doign in the notebook


    DATADIR = '/Users/pershing1/Programs/WATCHMAN/WbLS_3pct_QFitResults/'
    wload = wmi.WATCHMAKERSLoader(DATADIR)

    for bkg in dbc.PBKG_DATA_TYPES:
        bkg_data = wload.GetMergedDataPandasDF(bkg,treename='data',
                                               branches=dbc.BRANCHES)
    for sig in dbc.PSIG_DATA_TYPES:
        sig_data = wload.GetMergedDataPandasDF(sig,treename='data',
                                               branches=dbc.BRANCHES)

    pdf_cfgs = cfg["PDF_CONFIGS"]
    myCutManager = cm.CutManager(sig_data)
    for pdf in pdf_cfgs:
        prange = pdf_cfgs[pdf]["xrange"]
        myCutManager.ApplyCutValue(pdf,prange[0],"gte")
        myCutManager.ApplyCutValue(pdf,prange[1],"lte")
    sig_cuts = myCutManager.GetDataFrameWithCuts()
    myCutManager.LoadDataFrame(bkg_data)
    for pdf in pdf_cfgs:
        prange = pdf_cfgs[pdf]["xrange"]
        myCutManager.ApplyCutValue(pdf,prange[0],"gte")
        myCutManager.ApplyCutValue(pdf,prange[1],"lte")
    bkg_cuts = myCutManager.GetDataFrameWithCuts()
    print(myCutManager.GetListOfCurrentCuts())

    train_sig = sig_cuts[0:TRAINING_LENGTH]
    bkg_sig = bkg_cuts[0:TRAINING_LENGTH]
    test_sig = sig_cuts[TRAINING_LENGTH:TRAINING_LENGTH + TEST_LENGTH]
    test_bkg = bkg_cuts[TRAINING_LENGTH:TRAINING_LENGTH + TEST_LENGTH]

    #So, we now have data loaded into Pandas DataFrames and can make PDFs based on
    #The KDE fit.  They're not perfect, but good.  What needs to happen next...
    #  - Let's make a simple class that takes in the DataFrame, then applies cuts
    #    to the frame and keeps a log of what cuts are applied as you go.  This can
    #    be saved to the output to help log what prelim. cuts were applied.
    #  - Need to make KDE Estimate for all Signal and Background distributions based
    #    on what's in the config file.
    #  - Need to generate simulated datasets based on signal and background data that
    #    has not been used to make KDEs, and the operational schedule.  Start by just
    #    getting events past 3000.  Fill simulated events into a pandas dataframe.  
    #    Have the dataframe have: day, type_truth, [variables in config]
    #  - Make a class that takes in KDE estimates and calculates likelihood some 
    #    event data given is signal or background.
    #  - Make a HMM processor.  Needs to take in the likelihood class and use this as
    #    part of the HMM probability calculation.
    myLikelihoodCalculator = lc.LikelihoodCalculator()
    myLikelihoodCalculator.SetInterpolationType("linear")

    for pdf in pdf_cfgs:
        print("HAVE EACH PDF GET INITIALIZED HERE YO")
        print("THIS CONFIG SHOULD ALSO TELL WHAT VARIABLES TO LOAD INTO ROOTProcessor")
        print("OR, have some manual loading of parameters if it doesnt exist in config")
        pname = pdf
        prange = pdf_cfgs[pdf]["xrange"]
        pbw = pdf_cfgs[pdf]["bandwidth"]
        pbins = pdf_cfgs[pdf]["bins"]
        thex = np.arange(prange[0],prange[1],1)
        myestimator = ske.KernelDensityEstimator()
        myestimator.SetDataFrame(train_sig)
        if pbw is None:
            print("FINDING OPT. BANDWIDTH FOR %s"%(pname))
            pbw = myestimator.GetOptimalBandwidth(pname,[7,9],7)
            print("MY BW IS: " + str(pbw))
        #Perform kernel density estimation and then interpolate to form a function
        sx,sy = myestimator.KDEEstimate1D(pbw,pname,x_range=prange,bins=pbins,kern='gaussian')
        sy = sy/np.sum(sy)
        myLikelihoodCalculator.Add1DPDF(pname,"S",sx,sy)
        thehist,thehist_edges = np.histogram(train_sig[pname],bins=pbins,range=prange)
        print("THE HIST EDGES: " + str(thehist_edges))
        thehist = thehist/np.sum(thehist)
        print("SUM OF thehist: " + str(np.sum(thehist)))
        thehist_edges = thehist_edges[0:len(thehist_edges)-1]
        plt.plot(thehist_edges,thehist,label='data',alpha=0.7,linestyle='none',markersize=6,marker='o')
        plt.plot(sx,sy,label='KDE',alpha=0.7)
        plt.title("%s distribution for signal"%(pname))
        plt.legend()
        #plt.show()

        myestimator = ske.KernelDensityEstimator()
        train_bkg = bkg_cuts[0:TRAINING_LENGTH]
        myestimator.SetDataFrame(train_bkg)
        if pbw is None:
            print("FINDING OPT. BANDWIDTH FOR %s"%(pname))
            pbw = myestimator.GetOptimalBandwidth(pname,[1,7],7)
            print("MY BW IS: " + str(pbw))
        #Perform kernel density estimation 
        sx,sy = myestimator.KDEEstimate1D(pbw,pname,x_range=prange,bins=pbins,kern='gaussian')
        sy = sy/np.sum(sy)
        myLikelihoodCalculator.Add1DPDF(pname,"B",sx,sy)
        thehist,thehist_edges = np.histogram(train_bkg[pname],bins=pbins,range=prange)
        thehist = thehist/np.sum(thehist)
        print("SUM OF thehist: " + str(np.sum(thehist)))
        thehist_edges = thehist_edges[0:len(thehist_edges)-1]
        plt.plot(thehist_edges,thehist,label='data',alpha=0.7,linestyle='none',markersize=6,marker='o')
        plt.plot(sx,sy,label='KDE',alpha=0.7)
        plt.title("%s distribution for background"%(pname))
        plt.legend()
        #plt.show()
    #Neat.  We have the PDFs all made now and loaded them into our LikelihoodCalculator.  Let's test our
    #Likelihood calculator.
    plt.show()
    signal_lr = myLikelihoodCalculator.GetLikelihoods(test_sig)
    bkg_lr = myLikelihoodCalculator.GetLikelihoods(test_bkg)
    plt.hist(signal_lr,label="signal test data",bins=30,alpha=0.5)
    plt.hist(bkg_lr,label="background test data",bins=30,alpha=0.5)
    plt.legend(loc=2)
    plt.xlabel("Signal likelihood")
    plt.title("Likelihood distribution of signal and background data")
    plt.show()


