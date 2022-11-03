#!/usr/bin/env python3
"""
Description:

Example:
    %prog
    %prog
"""
# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
# Standard
import time
import sys
from traceback import print_exc

# Third party

# Local packages
from pyrowlib import pyrow


# Create a dictionary of the different status states
state = [
    "Error",
    "Ready",
    "Idle",
    "Have ID",
    "N/A",
    "In Use",
    "Pause",
    "Finished",
    "Manual",
    "Offline",
]

stroke = [
    "Wait for min speed",
    "Wait for acceleration",
    "Drive",
    "Dwelling",
    "Recovery",
]

workout = [
    "Waiting begin",
    "Workout row",
    "Countdown pause",
    "Interval rest",
    "Work time inverval",
    "Work distance interval",
    "Rest end time",
    "Rest end distance",
    "Time end rest",
    "Distance end rest",
    "Workout end",
    "Workout terminate",
    "Workout logged",
    "Workout rearm",
]

command = [
    "CSAFE_GETSTATUS_CMD",
    "CSAFE_PM_GET_STROKESTATE",
    "CSAFE_PM_GET_WORKOUTSTATE",
]


def conn2erg():
    """
    Connect to ergometer attacged to USB. If more than
    one erometer is attached then prompt for with selection.
    """
    erg = None
    try:
        ergs = list(pyrow.find())
        if len(ergs) == 0:
            raise Exception("No ergs found.")
        elif len(ergs) > 1:
            print("Please select the Ergometer to use:")
            for e in ergs:
                print(f"{str(e)}")
            sel = input("From this list")
        else:
            sel = ergs[0]
        erg = pyrow.pyrow(sel)
        if erg is None:
            raise Exception("Failed to create erg.")
    except Exception as err:
        print(str(err))
    finally:
        return erg


def main() -> int:
    ret = 0

    try:
        # Connecting to erg
        erg = conn2erg()
    except Exception:
        print_exc()
        ret = 1

    # prime status number
    cstate = -1
    cstroke = -1
    cworkout = -1

    erg.set_workout(distance=2000, split=100, pace=120)

    running = True
    interval = 1.0
    while running:
        try:
            results = erg.send(command)
            if cstate != (results["CSAFE_GETSTATUS_CMD"][0] & 0xF):
                cstate = results["CSAFE_GETSTATUS_CMD"][0] & 0xF
                print("State " + str(cstate) + ": " + state[cstate])
            if cstroke != results["CSAFE_PM_GET_STROKESTATE"][0]:
                cstroke = results["CSAFE_PM_GET_STROKESTATE"][0]
                print("Stroke " + str(cstroke) + ": " + stroke[cstroke])
            if cworkout != results["CSAFE_PM_GET_WORKOUTSTATE"][0]:
                cworkout = results["CSAFE_PM_GET_WORKOUTSTATE"][0]
                print("Workout " + str(cworkout) + ": " + workout[cworkout])
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nShutting Down\n")
            running = False
        except Exception as err:
            print(str(err))
            running = False
            ret = 1

    return ret


if __name__ == "__main__":
    sys.exit(main())
