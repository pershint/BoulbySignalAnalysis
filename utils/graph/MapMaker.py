import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def _AddOpMap(ScheduleDict,ax):
    '''Adds the operational map for the input experiment to the current plot'''
    #TODO: ADD THE DAYS WHERE A SHUTDOWN HAPPENS TO THE OP MAP
    schedule=ScheduleDict
    print(schedule)
    kshutoff_starts = np.empty(0)
    kshutoff_ends = np.empty(0)
    kmaint_starts = np.empty(0) 
    kmaint_ends = np.empty(0)
    killdays = np.empty(0)
    for core in schedule["SHUTDOWN_STARTDAYS"]:
        if core in schedule["CORETYPES"]["known_cores"]:
            kshutoff_starts = np.append(kshutoff_starts, \
                schedule["SHUTDOWN_STARTDAYS"][core])
            kshutoff_ends = kshutoff_starts + schedule["OFF_TIME"]
    for core in schedule["MAINTENANCE_STARTDAYS"]:
        if core in schedule["CORETYPES"]["known_cores"]:
            kmaint_starts = np.append(kmaint_starts, \
                     schedule["MAINTENANCE_STARTDAYS"][core])
            kmaint_ends = kmaint_starts + schedule["MAINTENANCE_TIME"]
    for j,core in enumerate(schedule["KILL_CORES"]):
        if core in schedule["CORETYPES"]["known_cores"]:
            killdays = np.append(killdays,schedule["KILL_DAYS"][j])

    print(killdays)
    if kshutoff_starts is not None:
        havesoffbox = False
        for j,val in enumerate(kshutoff_starts):
            if not havesoffbox:
                ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                    alpha=0.25, label="one off, shutdown\n truth")
                havesoffbox = True
            else:
                ax.axvspan(kshutoff_starts[j],kshutoff_ends[j], color='b', 
                    alpha=0.25)
    if kmaint_starts is not None and (int(schedule["MAINTENANCE_TIME"])>0):
        havemoffbox = False
        for j,val in enumerate(kmaint_starts):
            if not havemoffbox:
                ax.axvspan(kmaint_starts[j],kmaint_ends[j], 
                        color='orange', 
                    alpha=0.3, label="one off, maintenance\n truth")
                havemoffbox = True
            else:
                ax.axvspan(kmaint_starts[j],kmaint_ends[j], color='orange', 
                    alpha=0.3)
    if killdays is not None:
        havekillbox = False
        for j,val in enumerate(killdays):
            if not havekillbox:
                ax.axvspan(killdays[j],schedule["TOTAL_RUN"], color='red', 
                    alpha=0.3, label="Permanent shutdown\n truth")
                ax.vlines(x=killdays[j],ymin=-3, ymax=3,  
                color="red",
                linewidth=4,alpha=0.4)
                havemoffbox = True
            else:
                ax.axvspan(killdays[j],schedule["TOTAL_RUN"], color='red', 
                    alpha=0.3)
                ax.vlines(x=killdays[j], ymin=0, ymax=1, 
                color="red",linewidth=4,alpha=0.4)
    return ax

