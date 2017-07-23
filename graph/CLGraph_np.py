#This class takes in a dictionary of the format given running the "Analysis2"
#Class.  Functions are available for graphing the cumulative sum of
#determination days, the regions where a reactor was off, and the
#region a permanent shutdown begins.
#NOTE: self.schedule will contain entries for "FIRST_KNOWNSHUTDOWN",
#"FIRST_UNKNOWNSHUTDOWN","KILL_DAY","OFF_TIME","UP_TIME", and "TOTAL_RUN"
import numpy as np
import matplotlib.pyplot as plt

class Anal2_CLGraph(object):
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
        self.off_starts = []
        self.off_ends = []
        #Create arrays that have the outages of all reactors. These are
        #filled in and used in plots
        firstoff_days = {"known": self.schedule["FIRST_KNOWNSHUTDOWN"],
            "unknown": self.schedule["FIRST_UNKNOWNSHUTDOWN"]}
        off_time = self.schedule["OFF_TIME"]
        for firstoff in firstoff_days:
            off_day = firstoff_days[firstoff]
            while off_day < self.schedule["TOTAL_RUN"]:
                if self.schedule["KILL_DAY"] is not None:
                    if off_day > self.schedule["KILL_DAY"]:
                        break
                self.off_starts.append(off_day)
                self.off_ends.append(off_day + off_time)
                off_day = off_day + off_time + self.schedule["UP_TIME"]

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
        if self.off_starts is not None and self.off_ends is not None:
            haveoffbox = False
            for j,val in enumerate(self.off_starts):
                if not haveoffbox:
                    ax.axvspan(self.off_starts[j],self.off_ends[j], color='b', 
                        alpha=0.2, label="Reactor off")
                    haveoffbox = True
                else:
                    ax.axvspan(self.off_starts[j],self.off_ends[j], color='b', 
                        alpha=0.2)
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
        hand = [handles[0], handles[1], handles[3], handles[2], handles[4]]
        lab = [labels[0], labels[1], labels[3], labels[2], labels[4]]
        plt.legend(hand,lab, loc = 5)
        plt.show()
