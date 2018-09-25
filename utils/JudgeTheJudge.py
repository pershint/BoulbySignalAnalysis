#Here are some functions that take in a ForwardBackwardAnalysis Dict
#And evaluate how well the judge judged different aspects of the
#Reactor operation that actually happened!

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#Graphs that plot results from the Kalman Filter Analysis

def _reconstructPermShutdowns(ScheduleDict):
    schedule=ScheduleDict
    print(schedule)
    permshutdown_schedule = np.zeros(schedule["TOTAL_RUN"])
    killdays = np.empty(0)
    for j,core in enumerate(schedule["KILL_CORES"]):
        if core in schedule["CORETYPES"]["known_cores"]:
            killdays = np.append(killdays,schedule["KILL_DAYS"][j])
    for j,sstart in enumerate(killdays):
        permshutdown_schedule[int(sstart):len(permshutdown_schedule)] = 1
    print(permshutdown_schedule)
    return permshutdown_schedule

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
    kshutoff_ends = np.array(kshutoff_ends)
    kshutoff_starts = np.array(kshutoff_starts)
    for j,sstart in enumerate(kshutoff_starts):
        shutdown_schedule[int(kshutoff_starts[j])-1:int(kshutoff_ends[j])-1] = 1
    return shutdown_schedule

def _reconstructMaintenances(ScheduleDict):
    schedule=ScheduleDict
    print(schedule)
    maintenance_schedule = np.zeros(schedule["TOTAL_RUN"])
    kmaintoff_starts = np.empty(0)
    kmaintoff_ends = np.empty(0)
    for core in schedule["MAINTENANCE_STARTDAYS"]:
        if core in schedule["CORETYPES"]["known_cores"]:
            kmaintoff_starts = np.append(kmaintoff_starts, \
                schedule["MAINTENANCE_STARTDAYS"][core])
            kmaintoff_ends = kmaintoff_starts + schedule["MAINTENANCE_TIME"]
    kmaintoff_ends = np.array(kmaintoff_ends)
    kmaintoff_starts = np.array(kmaintoff_starts)
    for j,sstart in enumerate(kmaintoff_starts):
        maintenance_schedule[int(kmaintoff_starts[j])-1:int(kmaintoff_ends[j])-1] = 1
    return maintenance_schedule

def EvaluateJudgePerformance(ForwardBackAnalysisDict,optocheck="one off, shutdown"):
    '''Evaluates how well the judge has guessed the Large Shutdown periods, as well
    as the percentage of days that were misjudged as an off period'''
    JudgedRightPercentage = []
    FalseJudgePercentage = []
    LargeOffMap = _reconstructLargeShutdowns(ForwardBackAnalysisDict["schedule_dict_test"])
    PermOffMap = _reconstructPermShutdowns(ForwardBackAnalysisDict["schedule_dict_test"])
    MaintOffMap = _reconstructMaintenances(ForwardBackAnalysisDict["schedule_dict_test"])
    LargeOffMap = LargeOffMap + PermOffMap
    for j,offtype in enumerate(LargeOffMap):
        if offtype>1:
            LargeOffMap[j]=1
    Total_offdays = np.sum(LargeOffMap)
    print(Total_offdays)
    #Evaluate how many days were properly identified by the judge
    for j,predict in enumerate(ForwardBackAnalysisDict["Op_predictions"]):
        TheOpGuess = None
        try:
            TheOpGuess = predict[optocheck]
        except KeyError:
            print("The you specified was not checked by the judge.  Possible ops to choose:\n")
            print(predict.keys())
            return
        #Now we have this experiment's op.  Do the algorithms to test.
        Days_guessed_right = np.sum(LargeOffMap * TheOpGuess)
        JudgedRightPercentage.append(float(Days_guessed_right)/float(Total_offdays))

    #See if the judge claimed any full false shutdowns. If a maintenance outage
    #Occured during the time, the clock is reset
    shutdown_length = ForwardBackAnalysisDict["schedule_dict_test"]["OFF_TIME"]
    NoShuts_claimed = 0
    for j,predict in enumerate(ForwardBackAnalysisDict["Op_predictions"]):
        try:
            TheOpGuess = predict[optocheck]
        except KeyError:
            print("The you specified was not checked by the judge.  Possible ops to choose:\n")
            print(predict.keys())
            return
        LargeOffMap = np.array(LargeOffMap)
        AntiLargeOffMap = -1.0 * (LargeOffMap-1)
        #Now we have this experiment's op.  Do the algorithms to test.
        Days_falseclaim = (AntiLargeOffMap * TheOpGuess)
        daysinarowfalse = 0
        for j,day in enumerate(Days_falseclaim):
            if j==0:
                continue
            if Days_falseclaim[j] + Days_falseclaim[j-1] == 2:
                daysinarowfalse+=1
            #Relax our "False Claim" condition if a maintenance happens
            #within a month of a large shutdown
            if MaintOffMap[j] == 1 and np.sum(LargeOffMap[j-30:j+30])>0:
                daysinarowfalse=0
            else:
                daysinarowfalse=0
            if daysinarowfalse>shutdown_length:
                NoShuts_claimed+=1
    print("THE JUDGE MISCLAIMED %s SHUTDOWNS COMPLETELY"%str(NoShuts_claimed))
    #See if the judge missed any shutdowns completely
    shutdown_length = ForwardBackAnalysisDict["schedule_dict_test"]["OFF_TIME"]
    print("SHUTDOWN LENGTH IS %s"%(str(shutdown_length)))
    Shuts_missed = 0
    for j,predict in enumerate(ForwardBackAnalysisDict["Op_predictions"]):
        try:
            TheOpGuess = predict[optocheck]
        except KeyError:
            print("The you specified was not checked by the judge.  Possible ops to choose:\n")
            print(predict.keys())
            return
        TheOpGuess = np.array(TheOpGuess)
        NoJudge = -1.0 * (TheOpGuess-1)
        DaysNotJudged = NoJudge * LargeOffMap
        daysinarow_nojudge = 0
        for k,day in enumerate(DaysNotJudged):
            if k==0:
                continue
            if DaysNotJudged[k] + DaysNotJudged[k-1] == 2:
                daysinarow_nojudge+=1
            else:
                daysinarow_nojudge=0
            if daysinarow_nojudge>=(shutdown_length-1):
                Shuts_missed+=1
                print("MISSED A SHUT IN EXPT: " + str(j))
                daysinarow_nojudge=0
    print("THE JUDGE MISSED %s SHUTDOWNS COMPLETELY"%str(Shuts_missed))
    Average_Judgment = np.average(JudgedRightPercentage)*100.0
    print("THE JUDGED, ON AVERAGE, %s %% of shutdown days correctly!"%(str(Average_Judgment)))
    return

