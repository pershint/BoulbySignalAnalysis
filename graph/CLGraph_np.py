#This class takes in a dictionary of the format given running the "Analysis2"
#Class.  Functions are available for graphing the cumulative sum of
#determination days, the regions where a reactor was off, and the
#region a permanent shutdown begins.
#NOTE: self.schedule will contain entries for "FIRST_KNOWNSHUTDOWN",
#"FIRST_UNKNOWNSHUTDOWN","KILL_DAY","OFF_TIME","UP_TIME", and "TOTAL_RUN"
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class CLGraph(object):
    def __init__(self, AnalDict):
        self.site = AnalDict["Site"]
        self.pc = AnalDict["pc"] #fractional photocoverage
        self.schedule = AnalDict["schedule_dict"]
        self.kshutoff_starts = None
        self.kshutoff_ends = None
        self.kmaint_starts = None
        self.kmaint_ends = None
        self.ushutoff_starts = None
        self.ushutoff_ends = None
        self.umaint_starts = None
        self.umaint_ends = None
        if self.schedule["KILL_DAYS"] is not None:
            self.kill_days = self.schedule["KILL_DAYS"]
        else:
            self.kill_days = None
        
        #Initializes the off time plot elements for what is initially loaded
        self.init_offtimes()

    def clear_offtimes(self):
        #Clears knowledge of reactor outages so they are not plotted.
        self.kshutoff_starts = None
        self.kshutoff_ends = None
        self.kmaint_starts = None
        self.kmaint_ends = None
        self.kill_days = None

    def buildcsum(self, ddays):
        c = np.arange(1, len(ddays) + 1, 1)
        h = c/(float(len(ddays)-1))
        return h*100.0

    def init_offtimes(self):
        self.kshutoff_starts = np.empty(0)
        self.kshutoff_ends = np.empty(0)
        self.kmaint_starts = np.empty(0) 
        self.kmaint_ends = np.empty(0)
        for core in self.schedule["SHUTDOWN_STARTDAYS"]:
            if core in self.schedule["CORETYPES"]["known_cores"]:
                self.kshutoff_starts = np.append(self.kshutoff_starts, \
                    self.schedule["SHUTDOWN_STARTDAYS"][core])
                self.kshutoff_ends = self.kshutoff_starts + self.schedule["OFF_TIME"]
        for core in self.schedule["MAINTENANCE_STARTDAYS"]:
            if core in self.schedule["CORETYPES"]["known_cores"]:
                self.kmaint_starts = np.append(self.kmaint_starts, \
                         self.schedule["MAINTENANCE_STARTDAYS"][core])
                self.kmaint_ends = self.kmaint_starts + self.schedule["MAINTENANCE_TIME"]

    def plot_cumulsum(self,ddays,csum_vals,NumConfirmRequired=None,Title=None):
        #if the number of days required for confirmation was non-zero,
        #Need to shift the Cumulative distribution over
        #Plot the cumulative sum of determination days
        if NumConfirmRequired is not None:
            ddays = ddays -  NumConfirmRequired
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(ddays,csum_vals, color='green', alpha=0.8, 
                label="% CL",linewidth=4)
        if self.kill_days is not None:
            #FIXME: Want to have a label shoing which core shut down
            for kd in self.kill_days:
                ax.axvline(kd, color = "blue", alpha = 0.8, linewidth = 3, 
                        label="Permanent shutdown")
        #Add the CL lines
        CL_dict = {"68.3% CL": int(len(ddays) * 0.683), \
                 "95% CL": int(len(ddays) * 0.95), \
                 "99.7% CL": int(len(ddays) * 0.997)}
        CL_colors = ["m","k","r"]
        for j,CL in enumerate(CL_dict):
            ax.axvline(ddays[CL_dict[CL]], color = CL_colors[j], \
                    linewidth=2, label = CL)
        if self.kshutoff_starts is not None:
            havesoffbox = False
            for j,val in enumerate(self.kshutoff_starts):
                if not havesoffbox:
                    ax.axvspan(self.kshutoff_starts[j],self.kshutoff_ends[j], color='b', 
                        alpha=0.2, label="Large Shutdown")
                    havesoffbox = True
                else:
                    ax.axvspan(self.kshutoff_starts[j],self.kshutoff_ends[j], color='b', 
                        alpha=0.2)
        if self.kmaint_starts is not None:
            havemoffbox = False
            for j,val in enumerate(self.kmaint_starts):
                if not havemoffbox:
                    ax.axvspan(self.kmaint_starts[j],self.kmaint_ends[j], color='orange', 
                        alpha=0.4, label="Maintenance")
                    havemoffbox = True
                else:
                    ax.axvspan(self.kmaint_starts[j],self.kmaint_ends[j], color='orange', 
                        alpha=0.4)
        ax.set_xlim([0,np.max(ddays)])
        ax.set_ylim([0,100])
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        ax.set_xlabel("Experiment day", fontsize=18)
        ax.set_ylabel("Confidence Limit (%)", fontsize=18)
        ax.set_title(Title,fontsize=20)
        #The default order sucks.  I have to define it here
        handles, labels = ax.get_legend_handles_labels()
        hand = [handles[0], handles[1], handles[3], handles[2],\
                handles[4],handles[5]]
        lab = [labels[0], labels[1], labels[3], labels[2],\
                labels[4],labels[5]]
        for i in xrange(len(handles)-len(hand)): #add any extras
            hand.append(handles[len(hand)+i])
            lab.append(labels[len(lab)+i])
        plt.legend(hand,lab, loc = 2)
        plt.show()       

class OnOffCL(CLGraph):
    '''Plots the cumulative sum of a given analysis result dictionary's
    days of 3sigma determination.  If StackDicts given, a combination of
    results with the same run info. as the given analysis dict can all
    be plotted on top of each other.'''

    def __init__(self, AnalDict,StackDicts = None):
        super(OnOffCL, self).__init__(AnalDict)
        self.sd = StackDicts
        try:
            self.ddays = np.sort(AnalDict["determination_days"])
            self.no3sigs = AnalDict["no3sigmadays"]
        except KeyError:
            print("No rejection or acceptance of null hypothesis days present.")
            print("Are you loading the correct dictionary result type?")
            return
        self.num3SigRequired = AnalDict["num3siginarow"]
        self.csum_vals = self.buildcsum(self.ddays)
        self.plot_title = "Confidence Limit of days needed until WATCHMAN " + \
            "confirms on/off cycle at " + self.site + "\n" 
        #On init, run what the default is in the given dictionary
        self.plot_cumulsum(self.ddays, self.csum_vals,NumConfirmRequired= \
                self.num3SigRequired,Title=self.plot_title)

    def plot_stackCL(self, fixed_vardict={"buffersize":1.5, "pmt_type":"low_activity"},labelvar="pc"):
        if self.sd is None:
            print("You haven't initialized with an array of dictionaries in the class. Add them in.")
        sns.set_style("whitegrid")
        sns.axes_style("whitegrid")
        xkcd_colors = ['slate blue', 'light eggplant', 'warm pink', 'green', 'grass']
        sns.set_palette(sns.xkcd_palette(xkcd_colors))#,len(allclasssacs)))
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        #First, get all ddays in a dictionary w/ key as the varying variable
        colors = ["blue","purple","brown","red","orange","black","purple","pink","cyan","yellow"]
        plotdicts = []
        for results in self.sd:
            thisresdict = {}
            matchvars = True
            for var in fixed_vardict:
                if results[var] != fixed_vardict[var]:
                    matchvars = False
            if matchvars is True:
                thisentryindex = len(plotdicts)
                thisresdict["label"] = str(labelvar)+": "+str(results[labelvar])
                thisresdict["labelcolor"] = colors[thisentryindex]
                if self.num3SigRequired is not None:
                    thisresdict["ddays"] = np.sort(results["determination_days"]) - int(self.num3SigRequired)
                else:
                    thisresdict["ddays"] = np.sort(results["determination_days"])
                thisresdict["CL"] = thisresdict["ddays"][int(len(results["determination_days"]) * 0.95)]
                thisresdict["csum"] = self.buildcsum(thisresdict["ddays"])
                plotdicts.append(thisresdict)
        for results in plotdicts:
            print("RESULTS: " + str(results))
            ax.plot(results["ddays"], results["csum"], alpha=0.8,linewidth=4)

            ax.axvline(results["CL"], color=results["labelcolor"], \
                    linewidth=3, label = results["label"])
        if self.kill_days is not None:
            for kd in self.kill_days:
                ax.axvline(kd, color = "black", alpha = 0.8, linewidth = 3, 
                        label="Permanent shutdown")
        if self.kshutoff_starts is not None:
            havesoffbox = False
            for j,val in enumerate(self.kshutoff_starts):
                if not havesoffbox:
                    ax.axvspan(self.kshutoff_starts[j],self.kshutoff_ends[j], color='b', 
                        alpha=0.2, label="Large Shutdown")
                    havesoffbox = True
                else:
                    ax.axvspan(self.kshutoff_starts[j],self.kshutoff_ends[j], color='b', 
                        alpha=0.2)
        if self.kmaint_starts is not None:
            havemoffbox = False
            for j,val in enumerate(self.kmaint_starts):
                if not havemoffbox:
                    ax.axvspan(self.kmaint_starts[j],self.kmaint_ends[j], color='orange', 
                        alpha=0.4, label="Maintenance")
                    havemoffbox = True
                else:
                    ax.axvspan(self.kmaint_starts[j],self.kmaint_ends[j], color='orange', 
                        alpha=0.4)
        ax.set_xlim([0,800])
        ax.set_ylim([0,100])
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(24)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(24)
        ax.set_xlabel("Experiment day", fontsize=26)
        ax.set_ylabel("Confidence Limit (%)", fontsize=26)
        self.plot_title = "Confidence Limit of days needed until WATCHMAN " + \
            "confirms %s on/off cycle (Lines at 0.95 CL)\n" %self.site 
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
        self.csum_below_vals = self.buildcsum(self.belownulldays)
        self.csum_above_vals = self.buildcsum(self.abovenulldays)
        #On init, Plot the Cumulative distribution of rejection days
        self.plot_cumulsum(self.belownulldays, self.csum_below_vals,\
               Title=self.plot_title)
