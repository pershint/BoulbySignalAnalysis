#This should be run at start of main.  Will confirm that you have chosen
#A valid configuration to run the software.

def runchecks():
    if PHOTOCOVERAGE is not None and DETECTION_EFF is not None:
        print("CHOOSE EITHER A PHOTOCOVERAGE OR EFFICIENCY, NOT BOTH.")
        sys.exit(0)
    elif PHOTOCOVERAGE is not None:
        signals = dp.Signals_PC(PHOTOCOVERAGE, SITE)
        print(signals.signals)
    elif DETECTION_EFF is not None:
        signals = dp.Signals(DETECTION_EFF, SITE)
        print(signals.signals)
    elif DETECTION_EFF is None and PHOTOCOVERAGE is None:
        print("CHOOSE A PHOTOCOVERAGE OR EFFICIENCY YO")
        sys.exit(0)


