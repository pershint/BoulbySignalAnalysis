#This class takes in a dictionary of the format given running the "Analysis2"
#Class.  Functions are available for graphing the cumulative sum of
#determination days, the regions where a reactor was off, and the
#region a permanent shutdown begins.
#NOTE: self.schedule will contain entries for "FIRST_KNOWNSHUTDOWN",
#"FIRST_UNKNOWNSHUTDOWN","KILL_DAY","OFF_TIME","UP_TIME", and "TOTAL_RUN"
import numpy as np
import matplotlib.pyplot as plt

class CLGraph(object):
    def __init__(self, AnalDict):
        self.site = AnalDict["Site"]
        self.ddays = np.sort(AnalDict["determination_days"])
        self.no3sigs = AnalDict["no3sigmadays"]
        self.pc = AnalDict["pc"] #fractional photocoverage
        self.schedule = AnalDict["schedule_dict"]
        self.csum_vals = self.buildcsum(self.ddays)
        self.off_starts = None
        self.off_ends = None
        if self.schedule["KILL_DAY"] is not None:
            self.kill_day = self.schedule["KILL_DAY"]
        else:
            self.kill_day = None

    def buildcsum(self, ddays):
        c = np.arange(1, len(ddays) + 1, 1)
        h = c/(float(len(ddays)-1))
        return h*100.0

    def clear_offtimes(self):
        #Clears knowledge of reactor outages so they are not plotted.
        self.off_starts = None
        self.off_ends = None

    def init_offtimes(self):
        self.shutoff_starts = np.empty(0)
        self.shutoff_ends = np.empty(0)
        self.maint_starts = np.empty(0) 
        self.maint_ends = np.empty(0)
        for core in self.schedule["SHUTDOWN_STARTDAYS"]:
            self.shutoff_starts = np.append(self.shutoff_starts, \
                    self.schedule["SHUTDOWN_STARTDAYS"][core])
        self.shutoff_ends = self.shutoff_starts + self.schedule["OFF_TIME"]
        for core in self.schedule["MAINTENANCE_STARTDAYS"]:
            self.maint_starts = np.append(self.maint_starts, \
                    self.schedule["MAINTENANCE_STARTDAYS"][core])
        self.maint_ends = self.maint_starts + self.schedule["MAINTENANCE_TIME"]
        
    def plot_cumsum(self):
        #Plot the cumulative sum of determination days
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot((self.ddays - 13),self.csum_vals, color='green', alpha=0.8, 
                label="% CL",linewidth=4)
        if self.schedule["KILL_DAY"] is not None:
            ax.axvline(self.schedule["KILL_DAY"], color = "red", alpha = 0.8, 
                    label="Permanent shutdown")
        #Add the CL lines
        CL_dict = {"68.3% CL": int(len(self.ddays) * 0.683), \
                 "95% CL": int(len(self.ddays) * 0.95), \
                "99.7% CL": int(len(self.ddays) * 0.997)}
        CL_colors = ["m","k","r"]
        for j,CL in enumerate(CL_dict):
            ax.axvline(self.ddays[CL_dict[CL]] - 13, color = CL_colors[j], \
                    linewidth=2, label = CL)
        if self.shutoff_starts is not None:
            havesoffbox = False
            for j,val in enumerate(self.shutoff_starts):
                if not havesoffbox:
                    ax.axvspan(self.shutoff_starts[j],self.shutoff_ends[j], color='b', 
                        alpha=0.2, label="Large Shutdown")
                    havesoffbox = True
                else:
                    ax.axvspan(self.shutoff_starts[j],self.shutoff_ends[j], color='b', 
                        alpha=0.2)
        if self.maint_starts is not None:
            havemoffbox = False
            for j,val in enumerate(self.maint_starts):
                if not havemoffbox:
                    ax.axvspan(self.maint_starts[j],self.maint_ends[j], color='orange', 
                        alpha=0.4, label="Maintenance")
                    havemoffbox = True
                else:
                    ax.axvspan(self.maint_starts[j],self.maint_ends[j], color='orange', 
                        alpha=0.4)
        ax.set_xlim([0,np.max(self.ddays)])
        ax.set_ylim([0,100])
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        ax.set_xlabel("Experiment day", fontsize=18)
        ax.set_ylabel("Confidence Limit (%)", fontsize=18)
        ax.set_title("Confidence Limit of days needed until WATCHMAN " + 
            "confirms on/off cycle at " + self.site, fontsize=20)
        #The default order sucks.  I have to define it here
        handles, labels = ax.get_legend_handles_labels()
        hand = [handles[0], handles[1], handles[3], handles[2],\
                handles[4],handles[5]]
        lab = [labels[0], labels[1], labels[3], labels[2],\
                labels[4],labels[5]]
        plt.legend(hand,lab, loc = 5)
        plt.show()
