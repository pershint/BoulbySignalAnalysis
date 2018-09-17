#Here are some functions that take in a ForwardBackwardAnalysis Dict
#And evaluate how well the judge judged different aspects of the
#Reactor operation that actually happened!

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#Graphs that plot results from the Kalman Filter Analysis

def _reconstructLargeShutdowns(ScheduleDict):
    schedule=ScheduleDict
    print(schedule)
    shutdown_schedule = np.zeros(schedule["TOTAL_RUN"])
    kshutoff_starts = np.empty(0)
    kshutoff_ends = np.empty(0)
    for core in schedule["SHUTDOWN_STARTDAYS"]:
        if core in schedule["CORETYPES"]["known_cores"]:
            kshutoff_starts = np.append(kshutoff_starts, \
                schedule["SHUTDOWN_STARTDAYS"][core])
            kshutoff_ends = kshutoff_starts + schedule["OFF_TIME"]

    for j,sstart in enumerate(kshutoff_starts):
        shutdown_schedule[kshutoff_starts[j]:kshutoff_ends[j]] = 1
    return shutdown_schedule

