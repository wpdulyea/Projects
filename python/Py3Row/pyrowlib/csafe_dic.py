"""
Description:
"""
# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
# Standard
from enum import IntEnum

# Third party


# Local packages

# -----------------------------------------------------------------------------
#                           Global definitions
# -----------------------------------------------------------------------------

# Unique Frame Flags
eFSF = Extended_Frame_Start_Flag = 0xF0
sFSF = Standard_Frame_Start_Flag = 0xF1
SFF = Stop_Frame_Flag = 0xF2
BSF = Byte_Stuffing_Flag = 0xF3

# Frame status masking bytes
MASK_FRAME_TOGGLE = 0x80
MASK_PREVIOUS_FRAME_STATUS = 0x30
MASK_STATE_MACHINE_STATE = 0x0F

# PM-Specific CSAFE Command Wrappers
CSAFE_SETUSERCFG1_CMD = 0x1A
# PM Proprietary CSAFE Command Wrappers
CSAFE_SETPMCFG_CMD = 0x76
CSAFE_SETPMDATA_CMD = 0x77
CSAFE_GETPMCFG_CMD = 0x7E
CSAFE_GETPMDATA_CMD = 0x7F

# Dictionary of cmds['COMMAND_NAME'] = [0xCmd_Id, [Byte(s), ...]]
cmds = {}

# Short Commands
cmds["CSAFE_SETPMCFG_CMD"] = [0x76, []]
cmds["CSAFE_SETPMDATA_CMD"] = [0x77, []]
cmds["CSAFE_GETPMCFG_CMD"] = [0x7E, []]
cmds["CSAFE_GETPMDATA_CMD"] = [0x7F, []]
cmds["CSAFE_GETSTATUS_CMD"] = [0x80, []]
cmds["CSAFE_RESET_CMD"] = [0x81, []]
cmds["CSAFE_GOIDLE_CMD"] = [0x82, []]
cmds["CSAFE_GOHAVEID_CMD"] = [0x83, []]
cmds["CSAFE_GOINUSE_CMD"] = [0x85, []]
cmds["CSAFE_GOFINISHED_CMD"] = [0x86, []]
cmds["CSAFE_GOREADY_CMD"] = [0x87, []]
cmds["CSAFE_BADID_CMD"] = [0x88, []]
cmds["CSAFE_GETVERSION_CMD"] = [0x91, []]
cmds["CSAFE_GETID_CMD"] = [0x92, []]
cmds["CSAFE_GETUNITS_CMD"] = [0x93, []]
cmds["CSAFE_GETSERIAL_CMD"] = [0x94, []]
cmds["CSAFE_GETODOMETER_CMD"] = [0x9B, []]
cmds["CSAFE_GETERRORCODE_CMD"] = [0x9C, []]
cmds["CSAFE_GETTWORK_CMD"] = [0xA0, []]
cmds["CSAFE_GETHORIZONTAL_CMD"] = [0xA1, []]
cmds["CSAFE_GETCALORIES_CMD"] = [0xA3, []]
cmds["CSAFE_GETPROGRAM_CMD"] = [0xA4, []]
cmds["CSAFE_GETPACE_CMD"] = [0xA6, []]
cmds["CSAFE_GETCADENCE_CMD"] = [0xA7, []]
cmds["CSAFE_GETUSERINFO_CMD"] = [0xAB, []]
cmds["CSAFE_GETHRCUR_CMD"] = [0xB0, []]
cmds["CSAFE_GETPOWER_CMD"] = [0xB4, []]

# Long Commands
#
# Configuration (no affect)
cmds["CSAFE_AUTOUPLOAD_CMD"] = [0x01, [1]]
# Number of Digits
cmds["CSAFE_IDDIGITS_CMD"] = [0x10, [1]]
# Hour, Minute, Seconds
cmds["CSAFE_SETTIME_CMD"] = [0x11, [1, 1, 1]]
# Year, Month, Day
cmds["CSAFE_SETDATE_CMD"] = [0x12, [1, 1, 1]]
# State Timeout
cmds["CSAFE_SETTIMEOUT_CMD"] = [0x13, [1]]
# PM3 Specific Command (length computed)
cmds["CSAFE_SETUSERCFG1_CMD"] = [0x1A, [0]]
# Hour, Minute, Seconds
cmds["CSAFE_SETTWORK_CMD"] = [0x20, [1, 1, 1]]
# Distance, Units
cmds["CSAFE_SETHORIZONTAL_CMD"] = [0x21, [2, 1]]
# Total Calories
cmds["CSAFE_SETCALORIES_CMD"] = [0x23, [2]]
# Workout ID, N/A
cmds["CSAFE_SETPROGRAM_CMD"] = [0x24, [1, 1]]
# Stroke Watts, Units
cmds["CSAFE_SETPOWER_CMD"] = [0x34, [2, 1]]
# Capability Code
cmds["CSAFE_GETCAPS_CMD"] = [0x70, [1]]

# C2 Proprietary Short Commands using the
# CSAFE_SETUSERCFG1_CMD command wrapper
#
cmds["CSAFE_PM_GET_WORKOUTTYPE"] = [0x89, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_WORKOUTSTATE"] = [0x8D, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_INTERVALTYPE"] = [0x8E, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_WORKOUTINTERVALCOUNT"] = [0x9F, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_WORKTIME"] = [0xA0, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_WORKDISTANCE"] = [0xA3, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_ERRORVALUE"] = [0xC9, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_RESTTIME"] = [0xCF, [], CSAFE_SETUSERCFG1_CMD]

cmds["CSAFE_PM_GET_DRAGFACTOR"] = [0xC1, [], CSAFE_SETUSERCFG1_CMD]
cmds["CSAFE_PM_GET_STROKESTATE"] = [0xBF, [], CSAFE_SETUSERCFG1_CMD]

# C2 Proprietary Long Commands
#
# Time(0)/Distance(128), Duration
cmds["CSAFE_PM_SET_SPLITDURATION"] = [0x05, [1, 4], CSAFE_SETUSERCFG1_CMD]
# Block Length
cmds["CSAFE_PM_GET_FORCEPLOTDATA"] = [0x6B, [1], CSAFE_SETUSERCFG1_CMD]
# Disable(0)/Enable(1)
cmds["CSAFE_PM_SET_SCREENERRORMODE"] = [0x27, [1], CSAFE_SETUSERCFG1_CMD]
# Block Length
cmds["CSAFE_PM_GET_HEARTBEATDATA"] = [0x6C, [1], CSAFE_SETUSERCFG1_CMD]

# C2 Proprietary Short Commands using the
# CSAFE_GETPMCFG_CMD command wrapper
#
cmds["CSAFE_PM_GET_FW_VERSION"] = [0x80, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_HW_VERSION"] = [0x81, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_HW_ADDRESS"] = [0x82, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_TICK_TIMEBASE"] = [0x83, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_HRM"] = [0x84, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_DATETIME"] = [0x85, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_WORKOUTTYPE"] = [0x89, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_WORKOUTSTATE"] = [0x8D, [], CSAFE_GETPMCFG_CMD]
cmds["CSAFE_PM_GET_OPERATIONALSTATE"] = [0x8F, [], CSAFE_GETPMCFG_CMD]

# resp[0xCmd_Id] = [COMMAND_NAME, [Bytes, ...]]
# negative number for ASCII
# use absolute max number for variable, (getid & getcaps)
resp = {}

# Response Data to Short Commands
resp[0x80] = ["CSAFE_GETSTATUS_CMD", [0]]
resp[0x81] = ["CSAFE_RESET_CMD", [0]]
resp[0x82] = ["CSAFE_GOIDLE_CMD", [0]]
resp[0x83] = ["CSAFE_GOHAVEID_CMD", [0]]
resp[0x85] = ["CSAFE_GOINUSE_CMD", [0]]
resp[0x86] = ["CSAFE_GOFINISHED_CMD", [0]]
resp[0x87] = ["CSAFE_GOREADY_CMD", [0]]
resp[0x88] = ["CSAFE_BADID_CMD", [0]]
# Mfg ID, CID, Model, HW Version, SW Version
resp[0x91] = ["CSAFE_GETVERSION_CMD", [1, 1, 1, 2, 2]]
resp[0x92] = [
        "CSAFE_GETID_CMD", [-5]
    ]  # ASCII Digit (variable)
resp[0x93] = [
        "CSAFE_GETUNITS_CMD", [1]
    ]  # Units Type
resp[0x94] = [
        "CSAFE_GETSERIAL_CMD", [-9]
    ]  # ASCII Serial Number
resp[0x9B] = [
        "CSAFE_GETODOMETER_CMD", [4, 1]
    ]  # Distance, Units Specifier
resp[0x9C] = [
        "CSAFE_GETERRORCODE_CMD", [3]
    ]  # Error Code
resp[0xA0] = [
        "CSAFE_GETTWORK_CMD", [1, 1, 1]
        ]  # Hours, Minutes, Seconds
resp[0xA1] = [
        "CSAFE_GETHORIZONTAL_CMD", [2, 1]
    ]  # Distance, Units Specifier
resp[0xA3] = [
        "CSAFE_GETCALORIES_CMD", [2]
    ]  # Total Calories
resp[0xA4] = [
        "CSAFE_GETPROGRAM_CMD", [1]
    ]  # Program Number
resp[0xA6] = [
        "CSAFE_GETPACE_CMD", [2, 1]
    ]  # Stroke Pace, Units Specifier
resp[0xA7] = [
        "CSAFE_GETCADENCE_CMD", [2, 1]
    ]  # Stroke Rate, Units Specifier
resp[0xAB] = [
        "CSAFE_GETUSERINFO_CMD", [2, 1, 1, 1]
    ]  # Weight, Units Specifier, Age, Gender
resp[0xB0] = [
        "CSAFE_GETHRCUR_CMD", [1]
    ]  # Beats/Min
resp[0xB4] = [
        "CSAFE_GETPOWER_CMD", [2, 1]
    ]  # Stroke Watts

# Response Data to Long Commands
resp[0x01] = ["CSAFE_AUTOUPLOAD_CMD", [0]]
resp[0x10] = ["CSAFE_IDDIGITS_CMD", [0]]
resp[0x11] = ["CSAFE_SETTIME_CMD", [0]]
resp[0x12] = ["CSAFE_SETDATE_CMD", [0]]
resp[0x13] = ["CSAFE_SETTIMEOUT_CMD", [0]]
resp[0x1A] = [
        "CSAFE_SETUSERCFG1_CMD", [0]
    ]  # PM3 Specific Command ID
resp[0x20] = ["CSAFE_SETTWORK_CMD", [0]]
resp[0x21] = ["CSAFE_SETHORIZONTAL_CMD", [0]]
resp[0x23] = ["CSAFE_SETCALORIES_CMD", [0]]
resp[0x24] = ["CSAFE_SETPROGRAM_CMD", [0]]
resp[0x34] = ["CSAFE_SETPOWER_CMD", [0]]
resp[0x70] = [
        "CSAFE_GETCAPS_CMD", [11]
    ]  # Depended on Capability Code (variable)

# Response Data to PM3 Specific Short Commands
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x89] = [
        "CSAFE_PM_GET_WORKOUTTYPE", [1]
    ]  # Workout Type
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0xC1] = [
        "CSAFE_PM_GET_DRAGFACTOR", [1]
    ]  # Drag Factor
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0xBF] = [
        "CSAFE_PM_GET_STROKESTATE", [1]
    ]  # Stroke State
# Work Time (seconds * 100), Fractional Work Time (1/100)
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0xA0] = [
        "CSAFE_PM_GET_WORKTIME", [4, 1]
    ]
# Work Distance (meters * 10), Fractional Work Distance (1/10)
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0xA3] = [
        "CSAFE_PM_GET_WORKDISTANCE", [4, 1]
    ]
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0xC9] = [
        "CSAFE_PM_GET_ERRORVALUE", [2]
    ]  # Error Value
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x8D] = [
        "CSAFE_PM_GET_WORKOUTSTATE", [1]
    ]  # Workout State
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x9F] = [
        "CSAFE_PM_GET_WORKOUTINTERVALCOUNT", [1]
    ]  # Workout Interval Count
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x8E] = [
        "CSAFE_PM_GET_INTERVALTYPE", [1]
    ]  # Interval Type
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0xCF] = [
        "CSAFE_PM_GET_RESTTIME", [2]
    ]  # Rest Time

# Response Data to PM3 Specific Long Commands
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x05] = [
        "CSAFE_PM_SET_SPLITDURATION", [0]
    ]  # No variables returned !! double check
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x6B] = [
        "CSAFE_PM_GET_FORCEPLOTDATA",
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    ]  # Bytes read, data ...
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x27] = [
        "CSAFE_PM_SET_SCREENERRORMODE", [0]
    ]  # No variables returned !! double check
resp[(CSAFE_SETUSERCFG1_CMD << 8) + 0x6C] = [
        "CSAFE_PM_GET_HEARTBEATDATA",
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ]  # Bytes read, data ...
# Propietary Long command responses
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x80] = ["CSAFE_PM_GET_FW_VERSION", [15]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x81] = ["CSAFE_PM_GET_HW_VERSION", [15]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x82] = ["CSAFE_PM_GET_HW_ADDRESS", [4]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x83] = ["CSAFE_PM_GET_TICK_TIMEBASE", [4]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x84] = ["CSAFE_PM_GET_HRM", [1, 1, 1, 2]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x85] = ["CSAFE_PM_GET_DATETIME", [1, 1, 1, 1, 1, 2]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x89] = ["CSAFE_PM_GET_WORKOUTTYPE", [1]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x8D] = ["CSAFE_PM_GET_WORKOUTSTATE", [1]]
resp[(CSAFE_GETPMCFG_CMD << 8) + 0x8F] = ["CSAFE_PM_GET_OPERATIONALSTATE", [1]]


# -----------------------------------------------------------------------------
#                           State ENUMS
# -----------------------------------------------------------------------------
# Different status states


class OPERATIONAL_STATE(IntEnum):
    RESET = 0x00
    READY = 0x01
    WORKOUT = 0x02
    WARMUP = 0x03
    RACE = 0x04
    POWEROFF = 0x05
    PAUSE = 0x06
    INVOKEBOOTLOADER = 0x07
    POWEROFF_SHIP = 0x08
    IDLE_CHARGE = 0x09
    IDLE = 0x0A
    MFGTEST = 0x0B
    FWUPDATE = 0x0C
    DRAGFACTOR = 0x0D
    DFCALIBRATION = 0x64


class STATE_MACHINE_STATE(IntEnum):
    ERROR = 0x00
    READY = 0x01
    IDLE = 0x02
    HAVE_ID = 0x03
    IN_USE = 0x05
    PAUSE = 0x06
    FINISH = 0x07
    MANUAL = 0x08
    OFF_LINE = 0x09


class PREV_FRAME_STATUS(IntEnum):
    OK = 0x00
    REJECTED = 0x10
    BAD = 0x20
    NOT_READY = 0x30


class STROKE_STATE(IntEnum):
    WAITING_FOR_WHEEL_TO_REACH_MIN_SPEED_STATE = 0x00
    WAITING_FOR_WHEEL_TO_ACCELERATE_STATE = 0x01
    DRIVING_STATE = 0x02
    DWELLING_AFTER_DRIVE_STATE = 0x03
    RECOVERY_STATE = 0x04


class ROWING_STATE(IntEnum):
    INACTIVE = 0x00
    ACTIVE = 0x01


class WORKOUT_STATE(IntEnum):
    WAITTOBEGIN = 0x00
    WORKOUTROW = 0x01
    COUNTDOWNPAUSE = 0x02
    INTERVALREST = 0x03
    INTERVALWORKTIME = 0x04
    INTERVALWORKDISTANCE = 0x05
    INTERVALRESTENDTOWORKTIME = 0x06
    INTERVALRESTENDTOWORKDISTANCE = 0x07
    INTERVALWORKTIMETOREST = 0x08
    INTERVALWORKDISTANCETOREST = 0x09
    WORKOUTEND = 0x0A
    TERMINATE = 0x0B
    WORKOUTLOGGED = 0x0C
    REARM = 0x0D
