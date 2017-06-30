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
        return h

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
        ax.plot(self.ddays,self.csum_vals, color='green', alpha=0.8, 
                label="% CL")
        if self.schedule["KILL_DAY"] is not None:
            ax.axvline(self.schedule["KILL_DAY"], color = "red", alpha = 0.8, 
                    label="Permanent shutdown")
        if self.off_starts is not None and self.off_ends is not None:
            for j,val in enumerate(self.off_starts):
                ax.axvspan(self.off_starts[j],self.off_ends[j], color='m', 
                    alpha=0.2, label="Reactor off")
        ax.set_xlim([0,np.max(self.ddays)])
        ax.set_ylim([0,1])
        ax.set_xlabel("days")
        ax.set_ylabel("Confidence Limit")
        ax.set_title("Confidence Limit of days needed until WATCHMAN" + 
            "confirms on/off cycle at " + self.site)
        plt.legend(loc = 5)
        plt.show()
