# Functions take in an ExperimentalGenerator class and do various
#Fitting types.

import ROOT as r

def FillTH1D(h,data):
    '''
    Takes in a ROOT TH1D object and fills it with the input data.
    '''
    for element in data:
        h.Fill(element)
    return h

def PoissonFit(ExpGen):
    '''
    Takes in a generated experiment, and fits the candidate event
    Spectrum to a poisson distribution
    '''
    c1 = r.TCanvas("c1","c1",1200,1000)
    c1.Divide(1,1)
    c1.cd(1)
    x = ExpGen.experiment_days
    y = ExpGen.events
    h = r.TH1D('h','Events at Boulby site in WATCHMAN', 20, 0, 120)
    h = FillTH1D(h,y)
    h.Draw("al")
    pois_f = r.TF1('pois_f', '[0]*TMath::Power(([1]/[2]), (x/[2]))*(TMath::Exp(-([1]/[2])))/TMath::Gamma((x/[2])+1)', 0, 120.)
    pois_f.SetParameters(10,10,10)
    #Define the fit to fit to histogram of data
    h.Fit("pois_f","MR","",0.,110.)
    res = h.GetFunction("pois_f")
    #res.Draw("same")
    #print("CHI-SQUARE RESULT (RESULT/NDF): " + str(res.GetChisquare()) + "/" +
    #        str(res.GetNDF()))
    return c1, h


def PoissonFit_FixMean(ExpGen, lamb):
    '''
    Takes in a generated experiment, and fits the candidate event
    Spectrum to a poisson distribution of mean lamb.
    '''

