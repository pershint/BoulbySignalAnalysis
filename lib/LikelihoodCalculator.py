import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import seaborn as sns

class LikelihoodCalculator(object):
    '''
    Class that takes in 1D or 2D signal and background PDFs, developing a 
    classifier that returns the probability new input data comes from either
    the signal distributions or the background distributions.
    '''
    def __init__(self):
        self.PDFs = {}

    def RemovePDF(self,PDF_name):
        '''
        Remove this PDF from those used to calculate the likelihood.
        Input: PDF_name [string]
        '''
        if PDF_name not in self.PDFs.keys():
            print("PDF not loaded into likelihood function.")
        else:
            del self.PDFs[PDF_name]

    def GetPDFNames(self):
        PDF_names = []
        for PDF in self.PDFs:
            PDF_names.append(PDF)
        return PDF_names

    def Add1DPDF(self,PDF_name,datatype,x,y,label=None,weight=1.0):
        '''
        Adds information for a on3-dimensional PDF for use in the
        likelihood function.  xlabel and ylabel must correspond to
        labels in the DataFrame given to the GetLikelihood() method.
    
        Inputs:
            PDF_name [string]
                Name of this PDF distribution.  Should be kept consistent between
                signal "S" and background "B" inputs.
            datatype [string]
                PDF is associated with either the signal distribution or background
                distribution.  Allowed inputs are "S" or "B".
            label [string]
                x label to be shown.  Default is the same as PDF_name.
            x,y [array]
                Meshgrid relating data values (x) to the height of the PDF contour (y)

            weight [double]
                Weight of this PDF's contribution to the likelihood classifier.  
                Adjust the weights based on the rate of a particular signal or 
                background type.
        '''
        if label is None:
            label = PDF_name
        if PDF_name in self.PDFs.keys():
            if datatype in self.PDFs[PDF_name].keys():
                print("PDF %s of type %s already exists! Overwriting old PDF...")
        else:
            self.PDFs[PDF_name] = {}
        self.PDFs[PDF_name][datatype] = {}
        self.PDFs[PDF_name][datatype]['ntuple_label'] = label
        self.PDFs[PDF_name][datatype]['PDF_xdata'] = x
        self.PDFs[PDF_name][datatype]['PDF_ydata'] = y
        self.PDFs[PDF_name][datatype]['PDF_interpolation'] = None
        self.PDFs[PDF_name][datatype]["weight"] = weight
        self.PDFs[PDF_name][datatype]["dimension"] = 1

    def Add2DPDF(self,PDF_name,datatype,xlabel,ylabel,xx,yy,zz,weight=1.0):
        '''
        Adds information for a two-dimensional PDF for use in the
        likelihood function.  xlabel and ylabel must correspond to
        labels in the DataFrame given to the GetLikelihood() method.
    
        Inputs:
            PDF_name [string]
                Label for this particular PDF
            datatype [string]
                PDF is associated with either the signal or background
                distributions.  Allowed inputs are "S" or "B".
            xlabel,ylabel [string]
                X and Y labels for any plots generated using PDF.
            xx,yy,zz [array]
                Meshgrid relating x-axis and y-axis points to the height of the 
                contour
        '''
        if PDF_name in self.PDFs.keys():
            if datatype in self.PDFs[PDF_name].keys():
                print("PDF %s of type %s already exists! Overwriting old PDF...")
        self.PDFs[PDF_name][datatype] = {}
        self.PDFs[PDF_name][datatpye]['ntuple_xlabel'] = xlabel
        self.PDFs[PDF_name][datatpye]['ntuple_ylabel'] = ylabel
        self.PDFs[PDF_name][datatpye]['PDF_x'] = xx
        self.PDFs[PDF_name][datatpye]['PDF_y'] = yy
        self.PDFs[PDF_name][datatpye]['PDF_z'] = zz
        self.PDFs[PDF_name][datatpye]["weight"] = weight
        self.PDFs[PDF_name][datatpye]["dimension"] = 2
        self.PDFs[PDF_name][datatype]['PDF_interpolation'] = None

    def _Interpolate2DPDF(self,PDF_title,datatype,interpolation_type):
        PDF_info = self.PDFs[PDF_title][datatype]
        PDF_x = PDF_info['PDF_x']
        PDF_y = PDF_info['PDF_y']
        PDF_z = PDF_info['PDF_z']
        f = interpolate.interp2d(PDF_x,PDF_y,PDF_z,kind=interpolation_type)
        self.PDFs[PDF_title][datatype]["PDF_interpolation"] = f
        return

    def _Calculate2DLikelihoods(self,data,PDF_title,datatype,S_likelihood,B_likelihood):
        PDF_info = self.PDFs[PDF_title][datatype]
        PDF_weight = PDF_info['weight']
        f = self.PDFs[PDF_title][datatype]["PDF_interpolation"]
        x_data = data[PDF_info['ntuple_xlabel']]
        y_data = data[PDF_info['ntuple_ylabel']]
        if type(x_data[0]) == np.ndarray and type(y_data[0]) == np.ndarray:
            #Loop through data entries and for each entry, calculate this
            #PDF's contribution to the S or B likelihood
            for j,entry in enumerate(x_data):
                ev_xdata = x_data[j]
                ev_ydata = y_data[j]
                if len(ev_xdata) == 0: continue
                likelihood = f(ev_xdata,ev_ydata)
                likelihood = np.sum(likelihood)/len(likelihood)
                if datatype == "S":
                    S_likelihood[j]+=likelihood*PDF_weight
                elif datatype == "B":
                    B_likelihood[j]+=likelihood*PDF_weight
        else:
            #Loop through data entries and for each entry, calculate this
            #PDF's contribution to the S or B likelihood
            for k,entry in enumerate(x_data):
                ev_x= x_data[k]
                ev_y = y_data[k]
                likelihood = f(ev_x,ev_y)
                if datatype == "S":
                    S_likelihood[k]+=likelihood*PDF_weight
                elif datatype == "B":
                    B_likelihood[k]+=likelihood*PDF_weight
        return S_likelihood,B_likelihood

    def _Interpolate1DPDF(self,PDF_title,datatype,interpolation_type):
        PDF_info = self.PDFs[PDF_title][datatype]
        PDF_x = PDF_info['PDF_xdata']
        PDF_y = PDF_info['PDF_ydata']
        f = interpolate.interp1d(PDF_x,PDF_y,kind=PDF_interpolation)
        self.PDFs[PDF_title][datatype]["PDF_interpolation"] = f
        return

    def _Update1DLikelihoods(self,data,PDF_title,datatype,S_likelihood,B_likelihood):
        '''
        For each event in the data object, calculates the likelihood that the event 
        came from either the signal or background distribution of name PDF_title.
        Based on this, the likelihood that the event is either from the signal or
        background distributions is updated and returned.
        '''
        PDF_info = self.PDFs[PDF_title][datatype]
        PDF_weight = PDF_info['weight']
        f = PDF_info['PDF_interpolation']
        x_data = data[PDF_info['ntuple_label']]
        if type(x_data[0]) == np.ndarray:
            #Loop through data entries and for each entry, calculate this
            #PDF's contribution to the S or B likelihood
            for j,entry in enumerate(x_data):
                ev_xdata = x_data[j]
                if len(ev_xdata) == 0: continue
                likelihood = f(ev_xdata)
                likelihood = np.sum(likelihood)/len(likelihood)
                if datatype == "S":
                    S_likelihood[j]+=likelihood*PDF_weight
                elif datatype == "B":
                    B_likelihood[j]+=likelihood*PDF_weight
        else:
            #Loop through data entries and for each entry, calculate this
            #PDF's contribution to the S or B likelihood
            for k,entry in enumerate(x_data):
                ev_x= x_data[k]
                likelihood = f(ev_x)
                if datatype == "S":
                    S_likelihood[k]+=likelihood*PDF_weight
                elif datatype == "B":
                    B_likelihood[k]+=likelihood*PDF_weight
        return S_likelihood,B_likelihood

    ###FIXME: so I think that it could be good to generate the interpolated
    # PDFs separately.  This is likely something you only do once, whereas
    # getting likelihoods for different simulated WATCHMAN experiments 
    # may be done over and over again.
    def InterpolateAllPDFs(self):
        for PDF in self.PDFs:
            for datatype in self.PDFs[PDF]:
                if self.PDFs[PDF][datatype]["dimension"] == 1:
                    self._Interpolate1DPDF(PDF,datatype,PDF_interpolation)
                if self.PDFs[PDF][datatype]["dimension"] == 2:
                    self._Interpolate2DPDF(PDF,datatype,PDF_interpolation)

    def GetLikelihoods(self,test_data,PDF_interpolation='linear'):
        '''
        Using the signal and background data PDFs loaded, returns the 
        likelihood that each event in the test_data object 
        comes from the signal distribution 
        rather than the background distribution.
        '''
        likelihoods = []
        S_likelihood = np.zeros(len(test_data["entrynum"]))
        B_likelihood = np.zeros(len(test_data["entrynum"]))
        #Loop through 2D PDFs in class and calculate their likelihood contributions.
        #TODO: We should be able to restructure our inputs in a way to generalize to N-Dim. PDFs
        for PDF in self.PDFs:
            for datatype in self.PDFs[PDF]:
                if self.PDFs[PDF][datatype]["dimension"] == 1:
                    if self.PDFs[PDF][datatype]["PDF_interpolation"] is None:
                        self._Interpolate1DPDF(PDF,datatype,PDF_interpolation)
                    S_likelihood,B_likelihood = self._Update1DLikelihoods(test_data,PDF,datatype,S_likelihood,B_likelihood)
                if self.PDFs[PDF][datatype]["dimension"] == 2:
                    if self.PDFs[PDF][datatype]["PDF_interpolation"] is None:
                        self._Interpolate2DPDF(PDF,datatype,PDF_interpolation)
                    S_likelihood,B_likelihood = self._Calculate2DLikelihoods(test_data,PDF,datatype,S_likelihood,B_likelihood)
        Likelihood_ratio = (S_likelihood)/(S_likelihood + B_likelihood)
        return Likelihood_ratio 

    def OptimizeCut(self,S_likelihoods,B_likelihoods,l_range=[0,1],l_interval=0.01):
        '''
        TODO: Let's make this function something that chooses the optimal threshold 
        for the likelihood ratio to classify an event as either from the signal
        distribution or from the background distribution
        '''
        l_cuts = np.arange(l_range[0],l_range[1],l_interval)
        efficiencies = []
        purities = []
        lcuts_checked = []
        max_significance = 0
        max_sig_cut = None
        for l_cut in l_cuts:
            S_pass = float(len(np.where(S_likelihoods>l_cut)[0]))
            B_pass = float(len(np.where(B_likelihoods>l_cut)[0]))
            N0 = S_pass + B_pass
            if (N0 == 0):
                continue
            lcuts_checked.append(l_cut)
            eff = S_pass/len(S_likelihoods)
            purity = S_pass/(S_pass + B_pass)
            efficiencies.append(eff)
            purities.append(purity)

            #significance = eff * (purity**2)
            significance = eff*purity
            #significance = np.sqrt(2*N0*np.log(1+(S_pass/B_pass))-2*S_pass) 
            #significance = S_pass / np.sqrt(N0)
            #significance = S_pass/np.sqrt(B_pass)
            if max_sig_cut is None:
                max_sig_cut = l_cut
                max_significance = significance
            elif significance > max_significance:
                max_sig_cut = l_cut
                max_significance = significance
        print("USING EFFICIENCY*PURITY^2, MAX SIGNIFICANCE HAPPENS AT CUT %f"%(max_sig_cut))
        print("USING EFFICIENCY*PURITY^2, MAX SIGNIFICANCE IS %f"%(max_significance))
        return max_sig_cut, lcuts_checked, np.array(efficiencies), np.array(purities)

    def _GetOptimalPuritySqEff(self,training_input,training_output,PDF_name,PDF_interpolation):
        '''
        Determines the best purity^2*efficiency attainable if the likelihood 
        statistic is informed by the .
        '''
        S_likelihood = np.zeros(len(training_input["entrynum"]))
        B_likelihood = np.zeros(len(training_input["entrynum"]))
        self._Interpolate1DPDF(PDF_name,"S",PDF_interpolation)
        self._Interpolate1DPDF(PDF_name,"B",PDF_interpolation)
        S_likelihood,B_likelihood = self._Update1DLikelihoods(training_input,PDF_name,"S",S_likelihood,B_likelihood)
        S_likelihood,B_likelihood = self._Update1DLikelihoods(training_input,PDF_name,"B",S_likelihood,B_likelihood)
        Likelihood_ratio = (S_likelihood)/(S_likelihood + B_likelihood)
        #Now, let's plot the likelihoods for signal vs. background 
        b_only_test = np.where(training_output>0)[0]
        s_only_test = np.setdiff1d(np.arange(0,len(training_output),1),b_only_test)
        b_likelihoods = Likelihood_ratio[b_only_test]
        s_likelihoods = Likelihood_ratio[s_only_test]
        lcut_optimal, lcuts_checked, efficiencies, purities = self.OptimizeCut(s_likelihoods,b_likelihoods)
        optimal_index = np.where(lcuts_checked == lcut_optimal)[0]
        optimal_eff = efficiencies[optimal_index]
        optimal_purity = purities[optimal_index]
        return optimal_eff*optimal_purity*optimal_purity
