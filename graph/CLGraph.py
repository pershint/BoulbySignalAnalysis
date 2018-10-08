#This class takes in a dictionary of the format given running the "Analysis2"
#Class.  Functions are available for graphing the cumulative sum of
#determination days, the regions where a reactor was off, and the
#region a permanent shutdown begins.
#NOTE: self.schedule will contain entries for "FIRST_KNOWNSHUTDOWN",
#"FIRST_UNKNOWNSHUTDOWN","KILL_DAY","OFF_TIME","UP_TIME", and "TOTAL_RUN"
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import MapMaker as mm

class CLGraph(object):
    def __init__(self, AnalDict):
        self.site = AnalDict["Site"]
        self.pc = AnalDict["pc"] #fractional photocoverage
        self.schedule = AnalDict["schedule_dict"]
        
    def _buildcsum(self, ddays):
        c = np.arange(1, len(ddays) + 1, 1)
        h = c/(float(len(ddays)-1))
        return h*100.0

    def plot_cumulsum(self,ddays,csum_vals,NumConfirmRequired=None,Title=None,ShowOpMap=True):
        sns.set_style("whitegrid")
        #if the number of days required for confirmation was non-zero,
        #Need to shift the Cumulative distribution over
        #Plot the cumulative sum of determination days
        if NumConfirmRequired is not None:
            ddays = ddays -  NumConfirmRequired
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(ddays,csum_vals, color='green', alpha=0.8, 
                label="% CL",linewidth=4)
        #Add the CL lines
        CL_dict = {"68.3% CL": int(len(ddays) * 0.683), \
                 "95% CL": int(len(ddays) * 0.95), \
                 "99.7% CL": int(len(ddays) * 0.997)}
        print("THE CLS: ")
        for k in CL_dict:
            print("%s : %s"%(k,str(ddays[CL_dict[k]])))
        CL_colors = ["m","k","r"]
        for j,CL in enumerate(CL_dict):
            ax.axvline(ddays[CL_dict[CL]], color = CL_colors[j], \
                    linewidth=4, label = CL)
        if ShowOpMap:
            ax = mm._AddOpMap(self.schedule,ax)
        ax.set_xlim([0,np.max(ddays)+25])
        ax.set_ylim([0,100])
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(24)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(24)
        ax.set_xlabel("Experiment day", fontsize=28)
        ax.set_ylabel("Confidence Limit (%)", fontsize=28)
        ax.set_title(Title,fontsize=32)
        #The default order sucks.  I have to define it here
        handles, labels = ax.get_legend_handles_labels()
        hand = [handles[0], handles[1], handles[3], handles[2],\
                handles[4],handles[5]]
        lab = [labels[0], labels[1], labels[3], labels[2],\
                labels[4],labels[5]]
        for i in xrange(len(handles)-len(hand)): #add any extras
            hand.append(handles[len(hand)+i])
            lab.append(labels[len(lab)+i])
        legend = plt.legend(hand,lab, loc = 1,frameon=1,fontsize=20)
        frame = legend.get_frame()
        frame.set_facecolor("white")
        plt.show()       

class DwellTimeCL(CLGraph):
    '''Plots the cumulative sum of a given analysis result dictionary's
    days of 3sigma determination.  If StackDicts given, a combination of
    results with the same run info. as the given analysis dict can all
    be plotted on top of each other.'''

    def __init__(self, AnalDict):
        super(DwellTimeCL, self).__init__(AnalDict)
        self.sd = [AnalDict]
        try:
            self._ddays = np.sort(AnalDict["determination_days"])
            self._no3sigs = AnalDict["no3sigmadays"]
        except KeyError:
            print("No rejection or acceptance of null hypothesis days present.")
            print("Are you loading the correct dictionary result type?")
            return
        self._num3SigRequired = AnalDict["num3siginarow"]
        self._csum_vals = self._buildcsum(self._ddays)
        self.plot_title = "Confidence Limit of days needed until WATCHMAN \n" + \
            "confirms on/off cycle at " + self.site  
        #On init, run what the default is in the given dictionary
        self.plot_cumulsum(self._ddays, self._csum_vals,NumConfirmRequired= \
                self._num3SigRequired,Title=self.plot_title)

    def AddDictForStackPlot(self,AnalysisDict):
        '''Add a plot to the array for Stack Plotting'''
        self.sd.append(AnalysisDict)

    def LenStackPlotList(self):
        return len(self.sd)

    def ClearStackPlotList(self):
        self.sd = []

    def plot_stackCL(self, fixed_vardict={"buffersize":1.5, "pmt_type":"low_activity"},labelvar=["pc"]):
        if len(self.sd) <= 1:
            print("You must load in multiple DwellTime Analysis results to try and make this plot")
            return
        sns.set_style("whitegrid")
        xkcd_colors = ['blue', 'red', 'black', 'slate blue', 'light eggplant', 'warm pink', 'green', 'grass']
        sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        #First, get all ddays in a dictionary w/ key as the varying variable
        colors = ["blue","red","black","blue","red","black","black","pink","cyan","yellow"]
        plotdicts = []
        for results in self.sd:
            thisresdict = {}
            matchvars = True
            for var in fixed_vardict:
                if results[var] != fixed_vardict[var]:
                    matchvars = False
            if matchvars is True:
                thisentryindex = len(plotdicts)
                thisresdict["label"]=""
                for labels in labelvar:
                    thisresdict["label"] += " %s:%s"%(str(labels),results[labels])
                thisresdict["labelcolor"] = colors[thisentryindex]
                thisresdict["linecolor"] = colors[thisentryindex+len(self.sd)]
                if self.num3SigRequired is not None:
                    thisresdict["ddays"] = np.sort(results["determination_days"]) - int(self.num3SigRequired)
                else:
                    thisresdict["ddays"] = np.sort(results["determination_days"])
                thisresdict["CL"] = thisresdict["ddays"][int(len(results["determination_days"]) * 0.90)]
                thisresdict["csum"] = self._buildcsum(thisresdict["ddays"])
                plotdicts.append(thisresdict)
        for results in plotdicts:
            print("RESULTS: " + str(results))
            ax.plot(results["ddays"], results["csum"], color=results['linecolor'],alpha=0.8,linewidth=4)

            ax.axvline(results["CL"], color=results["labelcolor"], \
                    linewidth=3, label = results["label"])
        if ShowOpMap:
            ax = mm._AddOpMap(self.schedule,ax)
        ax.set_xlim([0,500])
        ax.set_ylim([0,100])
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(24)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(24)
        ax.set_xlabel("Experiment day", fontsize=26)
        ax.set_ylabel("Confidence Limit (%)", fontsize=26)
        self.plot_title = "Confidence Limit of days needed until WATCHMAN " + \
            "confirms %s on/off cycle (Lines at 0.90 CL)\n" %self.site 
        for var in fixed_vardict:
            self.plot_title+="%s: %s " % (str(var),str(fixed_vardict[var]))
        ax.set_title(self.plot_title,fontsize=32)
        plt.legend(loc = 1,fontsize=20)
        plt.show()       


class SPRTCL(CLGraph):
    def __init__(self, AnalDict):
        super(SPRTCL, self).__init__(AnalDict)
        try:
            self.belownulldays = np.sort(AnalDict["below_null_days"])
            self.abovenulldays = AnalDict["above_null_days"]
            self.nohypothesis = AnalDict["no_hypothesis"]
        except KeyError:
            print("No above or below days of null hypothesis present.")
            print("Are you loading the correct dictionary result type?")
            return
        self.plot_title = "Confidence Limit of days needed until WATCHMAN " + \
            "claims observation of reactor turn-off hypothesis at " + self.site 
        self.csum_below_vals = self._buildcsum(self.belownulldays)
        self.csum_above_vals = self._buildcsum(self.abovenulldays)
        #On init, Plot the Cumulative distribution of rejection days
        self.plot_cumulsum(self.belownulldays, self.csum_below_vals,\
               Title=self.plot_title)
