#!/usr/bin/env python3
"""
Description:

    PM5 Display:

    * Table of proportions
    x------>
  y ********TET**************SPM******
  | *Total Elaped Time | Strokes p/m *
  | **************PACE****************
  | *                                *
  v *  Cadence or Pace  /500m        *
    *                                *
    **********TM*************HR*******
    * Total Meters     | Heart Rate  *
    **************PLOT****************    *************APACE****************
    *                                *    *    Average Pace /500           *
    *                                *    ***************SM*****************
    *        optional Window(s)      * or *       Split Meter              *
    *                                *    **************PFM*****************
    *                                *    * Projected Finish/current Pace  *
    **********************************    **********************************
            y,   x,   h,   w 
    TET   = 0,   0,   1/7, 2/3            APACE  = 4/7, 0,  1/7,  3/3
    SPM   = 0,   2/3, 1/7, 1/3            SM     = 5/7, 0,  1/7,  3/3
    PACE  = 1/7, 0,   2/7, 3/3            PFM    = 6/7, 0,  2/7,  3/3
    TM    = 3/7, 0,   1/7, 2/3
    HR    = 3/7, 2/3, 1/7, 1/3
    PLOT  = 4/7, 0,   3/7, 3/3

 
"""
# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
# Standard
import sys
import os
import re
import math
from time import sleep
from traceback import format_exc
from random import randrange, sample, choice, randint, uniform
from datetime import datetime
from threading import Thread
from multiprocessing import Process
import curses

# Local packages
from pyrowlib import pyrow

# -----------------------------------------------------------------------------
#                           Global definitions
# -----------------------------------------------------------------------------
__author__ = "Copyright (c) 2022, W P Dulyea, All rights reserved."
__email__ = "wpdulyea@yahoo.com"
__version__ = "$Name: Release 0.1.0 $"[7:-2]

layouts = [
    "Standard with force curve",
    "Standard with projections",
]

# -----------------------------------------------------------------------------
#                               Classes
# -----------------------------------------------------------------------------
class Egometer(object):
    """ """

    def __init__(self):
        """ """
        ...


class Window(object):
    """
    Base class for a subwindow.
    """

    def __init__(
        self, caption: str, attr: int, h: int, w: int, x: int, y: int
    ):
        self._caption = caption
        self._capt_attr = attr
        self._width = w
        self._height = h
        self._y_pos = y
        self._x_pos = x

        try:

            self._window = curses.newwin(h, w, y, x)
            if "" != caption:
                self._add_caption()

            self._window.refresh()
        except Exception as err:
            raise err

    def _add_caption(self):
        try:
            self._window.box()
            # Position the optional caption to the upper left corner 1x1.
            self._window.addstr(
                1,
                1,
                str(self._caption),
                self._capt_attr,
            )
        except Exception as err:
            raise err

    def _add_label(self):
        try:
            # Calculate rough center
            max_y, max_x = self._window.getmaxyx()
            self._window.addstr(
                max_y // 2,
                (max_x - len(self._label)) // 2,
                str(self._label),
                self._label_attr,
            )
        except Exception as err:
            raise err

    def set_bkgd(self, ch, attr=0):
        self._window.bkgd(ch, attr)

    def add_win_label(self, label: str, attr: int):
        """
        Add the string to the center, with BOLD flavoring.
        """
        self._label = label
        self._label_attr = attr

        self._add_label()

    def redraw(self):
        try:
            # self._window.clear()
            self._window.box()
            self._add_caption()
            self._add_label()

            # Might need to add some code to repaint the window on terminal resize
            # if supported.
            self._window.refresh()
        except Exception as err:
            raise err

    def refresh(self):
        self._window.refresh()


class Element(Window):
    """
    Represents each element of displayed data for PM Monitor.
    """

    _value = 0
    _attr = 0

    def refresh_value(self, value):
        self._value = value
        self.add_win_label(value, self._attr)

    def get_value(self):
        return self._value


class ForceCurve(Window):
    """ """

    _pchar = "*"
    # Colours for each plot to maintain per stroke
    _pColours = list()
    _count = 0
    # Record each plot up to len of pColours. Once len of each is == then clean
    # lastPlot [] = [y_pos, x_pos, colour_attr]
    _lastPlot = list()

    def update_forcecurve(self, data: list):
        """
        Given a forcecuve data list, plot to window.

        This will redraw the last plot up to pre-defined forceplots
        defaults to 4 in different colours.
        """
        y_plot = 0
        y_max, x_max = self._window.getmaxyx()
        x_plot = x_max // len(data)  # which should be 32

        # ToDo: It is not clear where this value comes from.
        max_force = 300
        force_unit = y_max // max_force

        if len(self._lastPlot) >= 4:
            self._lastPlot = [[]]
            self._count = 0

        for d in data:
            y_plot = self.max_y - (d * force_unit)
            self._lastPlot[self._count].append(
                [y_plot, x_plot, self.pColours[self.count]]
            )
        self._count += 1
        # Extend the list for the next plot
        self._lastPlot.append([])

    def draw_forcecurve(self):
        """
        if self.lastPlot is not empty, repaint the contents to the window
        """
        for plot in self._lastPlot[0 : len(self._lastPlot)]:
            for curve in plot:
                #                    [y_pos,    x_pos,        char, colour_attr]
                self.window.addstr(curve[0], curve[1], self._pchar, curve[2])


# -----------------------------------------------------------------------------
#                               Functions
# -----------------------------------------------------------------------------
def conn2erg():
    """
    Connect to ergometer attacged to USB. If more than
    one erometer is attached then prompt for with selection.
    """
    erg = None
    try:
        ergs = list(usberg.find())
        if len(ergs) == 0:
            raise Exception("No ergs found.")
        elif len(ergs) > 1:
            print("Please select the Ergometer to use:")
            for e in ergs:
                print(f"{str(e)}")
            sel = input("From this list")
        else:
            sel = ergs[0]
        erg = pyrow.PyRow(sel)
        if erg is None:
            raise Exception("Failed to create erg.")
    except Exception as err:
        print(str(err))
    finally:
        return erg


def read_inputs():
    from argparse import ArgumentParser

    res = None
    try:
        parser = ArgumentParser()
        parser.add_argument(
            "-a", help="Is for Apple", type=str, required=False
        )
        parser.add_argument(
            "-b", help="Is for how many Ballon(s)", type=int, required=True
        )
        res = parser.parse_args()
    except Exception as error:
        print(str(error))
    finally:
        return res


def main(stdscr):
    # Initialize the curses.
    stdscr = curses.initscr()
    stdscr.refresh()
    stdscr.box()
    # Do not echo keys.
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)

    if curses.has_colors():
        curses.start_color()

    stdscr.keypad(True)

    bgColors = [
        curses.COLOR_BLUE,
        curses.COLOR_CYAN,
        curses.COLOR_GREEN,
        curses.COLOR_MAGENTA,
        curses.COLOR_RED,
        curses.COLOR_YELLOW,
        curses.COLOR_RED | curses.COLOR_YELLOW,
        curses.COLOR_BLUE | curses.COLOR_WHITE,
        curses.COLOR_GREEN | curses.COLOR_YELLOW,
    ]
    # Random selection of colours
    colors = sample(bgColors, 6)

    # Create ncurses color pair objects.
    curses.init_pair(1, curses.COLOR_WHITE, colors[0])
    curses.init_pair(2, curses.COLOR_WHITE, colors[1])
    curses.init_pair(3, curses.COLOR_WHITE, colors[2])
    curses.init_pair(4, curses.COLOR_WHITE, colors[3])
    curses.init_pair(5, curses.COLOR_WHITE, colors[4])
    curses.init_pair(6, curses.COLOR_WHITE, colors[5])

    caughtExceptions = ""
    try:
        window1 = []
        window2 = []
        window3 = []
        window4 = []
        window5 = []
        window6 = []

        window1Obj = None
        window2Obj = None
        window3Obj = None
        window4Obj = None
        window5Obj = None
        window6Obj = None

        window1Caption = "Total Elapsed Time"
        window2Caption = "Stroke Per Minute"
        window3Caption = "Splits (Time per 500m)"
        window4Caption = "Total Meters"
        window5Caption = "Heart Rate"
        window6Caption = "Force Curve"

        # Window dimensions will be proportinally based
        # as illustgrated in top of file.
        #         y,   x,   w,   h
        # ==========================
        # Win-1 = 0,   0,   2/3, 1/7
        # Win-2 = 0,   2/3, 1/3, 1/7
        # Win-3 = 1/7, 0,   3/3, 2/7
        # Win-4 = 3/7, 0,   2/3, 1/7
        # Win-5 = 3/7, 2/3, 1/3, 1/7
        # Win-6 = 4/7, 0,   3/3, 3/7
        #
        minWindowWidth = curses.COLS * 1 // 3
        maxWindowWidth = curses.COLS * 2 // 3
        minWindowHeight = curses.LINES * 1 // 7
        maxWindowHeight = curses.LINES * 3 // 7

        # Select a layout.
        chosenLayout = layouts[0]
        match chosenLayout:
            case "Standard with force curve":
                # Windows 1 and 2 will be the top, Window 3 will be the bottom.
                window1 = [0, 0, curses.COLS - minWindowWidth, minWindowHeight]
                window2 = [0, window1[2], minWindowWidth, minWindowHeight]
                window3 = [
                    minWindowHeight,
                    0,
                    curses.COLS,
                    minWindowHeight * 2,
                ]
                window4 = [
                    minWindowHeight * 3,
                    0,
                    maxWindowWidth,
                    minWindowHeight,
                ]
                window5 = [
                    minWindowHeight * 3,
                    maxWindowWidth,
                    curses.COLS - maxWindowWidth,
                    minWindowHeight,
                ]
                window6 = [
                    minWindowHeight * 4,
                    0,
                    curses.COLS,
                    curses.LINES - minWindowHeight * 4,
                ]

                window6Caption = chosenLayout + " - Press a key to quit."
            case _:
                raise Exception("oops!, no mtching case")

        # SETUP PM VARS
        total_meters = 0
        spm = 0
        pace_mins = 0
        pace_secs = 0
        wtime = 0
        wtime_mins = 0
        wtime_secs = 0
        hrate = 0
        srate = 0
        calhr = 0
        calories = 0
        # Create and refresh each window. Put the caption 2 lines up from bottom
        # in case it wraps. Putting it on the last line with no room to wrap (if
        # the window is too narrow for the text) will cause an exception.
        window1Obj = Window(
            window1Caption,
            curses.color_pair(1) | curses.A_BOLD,
            window1[3],
            window1[2],
            window1[1],
            window1[0],
        )
        window1Obj.set_bkgd(" ", curses.color_pair(1) | curses.A_BOLD)
        window1Obj.add_win_label(
            "%.2d:%.2d" % (wtime_mins, wtime_secs),
            curses.color_pair(1) | curses.A_BOLD,
        )
        window1Obj.refresh()

        window2Obj = Window(
            window2Caption,
            curses.color_pair(2) | curses.A_BOLD,
            window2[3],
            window2[2],
            window2[1],
            window2[0],
        )
        window2Obj.set_bkgd(" ", curses.color_pair(2) | curses.A_BOLD)
        window2Obj.add_win_label(
            "%.2d /spm" % (srate), curses.color_pair(2) | curses.A_BOLD
        )
        window2Obj.refresh()

        window3Obj = Window(
            window3Caption,
            curses.color_pair(3) | curses.A_BOLD,
            window3[3],
            window3[2],
            window3[1],
            window3[0],
        )
        window3Obj.set_bkgd(" ", curses.color_pair(3) | curses.A_BOLD)
        window3Obj.add_win_label(
            "%.2d:%.2d /500m" % (pace_mins, pace_secs),
            curses.color_pair(3) | curses.A_BOLD,
        )
        window3Obj.refresh()

        window4Obj = Window(
            window4Caption,
            curses.color_pair(4) | curses.A_BOLD,
            window4[3],
            window4[2],
            window4[1],
            window4[0],
        )
        window4Obj.set_bkgd(" ", curses.color_pair(4) | curses.A_BOLD)
        window4Obj.add_win_label(
            "%.4d m" % (total_meters), curses.color_pair(4) | curses.A_BOLD
        )
        window4Obj.refresh()

        window5Obj = Window(
            window5Caption,
            curses.color_pair(5) | curses.A_BOLD,
            window5[3],
            window5[2],
            window5[1],
            window5[0],
        )
        window5Obj.set_bkgd(" ", curses.color_pair(5) | curses.A_BOLD)
        window5Obj.add_win_label(
            "%.3d bpm" % (hrate), curses.color_pair(5) | curses.A_BOLD
        )
        window5Obj.refresh()

        window6Obj = ForceCurve(
            window6Caption,
            curses.color_pair(6) | curses.A_BOLD,
            window6[3],
            window6[2],
            window6[1],
            window6[0],
        )
        window6Obj.set_bkgd(" ", curses.color_pair(6) | curses.A_BOLD)
        window6Obj.add_win_label("Watts", curses.color_pair(6) | curses.A_BOLD)
        window6Obj.refresh()
        stdscr.nodelay(True)

        ch = 0
        while ch != ord("q"):
            ch = window6Obj._window.getch()
            if ch < 0:
                ch = 0
            stdscr.timeout(3000)

        # Debugging output.
        stdscr.addstr(0, 0, "Chosen layout is [" + chosenLayout + "]")
        stdscr.addstr(1, 10, "Window 1 params are [" + str(window1) + "]")
        stdscr.addstr(2, 10, "Window 2 params are [" + str(window2) + "]")
        stdscr.addstr(3, 10, "Window 3 params are [" + str(window3) + "]")
        stdscr.addstr(4, 10, "Window 4 params are [" + str(window4) + "]")
        stdscr.addstr(5, 10, "Window 5 params are [" + str(window5) + "]")
        stdscr.addstr(6, 10, "Window 6 params are [" + str(window6) + "]")
        stdscr.addstr(7, 10, "Colors are [" + str(colors) + "]")
        stdscr.addstr(8, 0, "Press a key to continue.")
        stdscr.refresh()
        stdscr.getch()
    except Exception:
        caughtExceptions = format_exc()

    finally:
        # Debugging output.
        stdscr.addstr(0, 0, "Chosen layout is [" + chosenLayout + "]")
        stdscr.addstr(1, 10, "Window 1 params are [" + str(window1) + "]")
        stdscr.addstr(2, 10, "Window 2 params are [" + str(window2) + "]")
        stdscr.addstr(3, 10, "Window 3 params are [" + str(window3) + "]")
        stdscr.addstr(4, 10, "Window 4 params are [" + str(window4) + "]")
        stdscr.addstr(5, 10, "Window 5 params are [" + str(window5) + "]")
        stdscr.addstr(6, 10, "Window 6 params are [" + str(window6) + "]")
        stdscr.addstr(7, 10, "Colors are [" + str(colors) + "]")
        stdscr.addstr(8, 0, "Press a key to continue.")
        stdscr.refresh()
        stdscr.getch()

        # End of Program...
        # Turn off cbreak mode...
        curses.nocbreak()

        # Turn echo back on.
        curses.echo()

        # Restore cursor blinking.
        curses.curs_set(True)

        # Turn off the keypad...
        # stdscr.keypad(False)

        # Restore Terminal to original state.
        curses.endwin()

        # Display Errors if any happened:
        if "" != caughtExceptions:
            print("Got error(s) [" + caughtExceptions + "]")
            return 1
        else:
            return 0


# -----------------------------------------------------------------------------
#                               If run as main file
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    cmd_name = os.path.splitext(os.path.basename(__file__))[0]
    args = read_inputs()
    if args is None:
        raise Exception
        sys.exit(1)

    try:
        curses.wrapper(main)

    except Exception as err:
        print(str(err))
        print(format_exc())
        sys.exit(1)
