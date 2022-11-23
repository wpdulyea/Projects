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
import math
from traceback import format_exc
from random import randrange, sample, choice, randint, uniform
from datetime import datetime
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
class Window(object):
    """
    Base class for a subwindow.
    """

    def __init__(self, caption: str, attr: int, cords: list):
        self._caption = caption
        self._capt_attr = attr
        self._cords = cords

        self._window = curses.newwin(*cords)
        if "" != caption:
            self._add_caption()

        self._window.refresh()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def get_cordinates(self):
        return self._cords

    def _add_caption(self):
        self._window.box()
        # Position the optional caption to the upper left corner 1x1.
        self._window.addstr(
            1,
            1,
            str(self._caption),
            self._capt_attr,
        )

    def _add_label(self):
        # Calculate rough center
        max_y, max_x = self._window.getmaxyx()
        self._window.addstr(
            max_y // 2,
            (max_x - len(self._label)) // 2,
            str(self._label),
            self._label_attr,
        )

    def set_bkgd(self, ch, attr=0):
        self._window.bkgd(ch, attr)

    def add_win_label(self, label: str, attr: int):
        """
        Add the string to the center, with BOLD flavoring.
        """
        self._label = label
        self._label_attr = attr

        self._add_label()

    def update_label(self: object, label: str):
        self._label = label
        self._add_label()
        self.refresh()

    def redraw(self):
        self._window.clear()
        self._window.box()
        self._add_caption()
        self._add_label()

        # Might need to add some code to repaint the window on terminal
        # resize if supported.
        self._window.refresh()

    def refresh(self):
        self._window.refresh()


class ForceCurve(Window):
    """ """

    _pchar = "+"
    _count = 0
    # Record each plot up to len of pColours. Once len of each is == then clean
    # lastPlot [] = [y_pos, x_pos, colour_attr]
    _lastPlot = [[]]

    def __init__(
        self, caption: str, attr: int, cords: list, plotColours: list
    ):
        super().__init__(caption, attr, cords)
        self._pColours = plotColours

    def update_forcecurve(self, data: list):
        """
        Given a forcecuve data list, plot to temp storage .

        This will redraw the last plot up to pre-defined forceplots
        defaults to 4 in different colours.
        """
        y_plot = x_plot = 2
        y_max, x_max = self._window.getmaxyx()
        y_max -= 2
        x_max -= 2
        x_step = 1

        # ToDo: It is not clear where this value comes from.
        max_force = 300
        if y_max < max_force:
            y_scaled = y_max / max_force
        else:
            y_scaled = 1

        if self._count >= 3:
            self._lastPlot = [[]]
            self._count = 0
        else:
            self._lastPlot.append([])

        for d in data:
            y_plot = y_max - math.floor(d * y_scaled)
            self._lastPlot[self._count].append(
                [y_plot, x_plot, self._pColours[self._count]]
            )
            x_plot += x_step

        self._count += 1

    def redraw(self):
        """
        if self.lastPlot is not empty, repaint the contents to the window
        """
        super().redraw()

        # ToDo: This may not work if window resizing is added.
        for plot in self._lastPlot[0 : len(self._lastPlot)]:
            for curve in plot:
                if len(curve) == 3:
                    # curve[y_pos, x_pos, char, colour_attr]
                    self._window.addstr(
                        curve[0], curve[1], self._pchar, curve[2]
                    )
                else:
                    # quietly skip
                    pass

        self.refresh()


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
        erg = pyrow.PyRow(sel)
        if erg is None:
            raise Exception("Failed to create erg.")
    except Exception as err:
        raise err
    finally:
        return erg


def parse_options():
    from argparse import ArgumentParser

    res = None
    try:
        parser = ArgumentParser()
        parser.add_argument(
            "-a", help="Is for Apple", type=str, required=False
        )
        parser.add_argument(
            "-b", help="Is for how many Ballon(s)", type=int, required=False
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

    # Curses colours.
    curses.init_pair(1, curses.COLOR_WHITE, colors[0])
    curses.init_pair(2, curses.COLOR_WHITE, colors[1])
    curses.init_pair(3, curses.COLOR_WHITE, colors[2])
    curses.init_pair(4, curses.COLOR_WHITE, colors[3])
    curses.init_pair(5, curses.COLOR_WHITE, colors[4])
    curses.init_pair(6, curses.COLOR_WHITE, colors[5])

    # Monitor windows
    tet_win = None
    spm_win = None
    splits_win = None
    tm_win = None
    hr_win = None
    fc_win = None

    tet_cords = []
    spm_cords = []
    splits_cords = []
    tm_cords = []
    hr_cords = []
    fc_cords = []

    tet_caption = "Total Elapsed Time"
    spm_caption = "Stroke Per Minute"
    splits_caption = "Splits (Time per 500m)"
    tm_caption = "Total Meters"
    hr_caption = "Heart Rate"
    fc_caption = "Force Curve"

    chosenLayout = ""
    caughtExceptions = ""
    try:
        erg = conn2erg()
        if erg is None:
            raise Exception("Failed to connect with erg")

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
        minWidth = curses.COLS * 1 // 3
        maxWidth = curses.COLS * 2 // 3
        minHeight = curses.LINES * 1 // 7
        maxHeight = curses.LINES * 3 // 7

        # Select a layout.
        chosenLayout = layouts[0]
        match chosenLayout:
            case "Standard with force curve":
                # Windows [height, width, y, x]
                tet_cords = [minHeight, curses.COLS - minWidth, 0, 0]
                spm_cords = [minHeight, minWidth, 0, tet_cords[1]]
                splits_cords = [
                    minHeight * 2,
                    curses.COLS,
                    minHeight,
                    0,
                ]
                tm_cords = [
                    minHeight,
                    maxWidth,
                    maxHeight - 1,
                    0,
                ]
                hr_cords = [
                    minHeight,
                    curses.COLS - maxWidth,
                    maxHeight - 1,
                    maxWidth,
                ]
                fc_cords = [
                    curses.LINES - minHeight * 4,
                    curses.COLS,
                    minHeight * 4,
                    0,
                ]

                Exit_Caption = chosenLayout + " - Press a key to quit."
            case _:
                raise Exception("oops!, no mtching case")

        # PM vars
        total_meters = 0
        pace_mins = 0
        pace_secs = 0
        wtime_mins = 0
        wtime_secs = 0
        hrate = 0
        srate = 0
        power = 0
        cals_hr = 0
        cals = 0

        # Create each window to display erg data.
        with Window(
            tet_caption, curses.color_pair(1) | curses.A_BOLD, tet_cords
        ) as tet_win:
            tet_win.set_bkgd(" ", curses.color_pair(1) | curses.A_BOLD)
            tet_win.add_win_label(
                "%.2d:%.2d" % (wtime_mins, wtime_secs),
                curses.color_pair(1) | curses.A_BOLD,
            )
            tet_win.refresh()

        with Window(
            spm_caption, curses.color_pair(2) | curses.A_BOLD, spm_cords
        ) as spm_win:
            spm_win.set_bkgd(" ", curses.color_pair(2) | curses.A_BOLD)
            spm_win.add_win_label(
                "%.2d /spm" % (srate), curses.color_pair(2) | curses.A_BOLD
            )
            spm_win.refresh()

        with Window(
            splits_caption, curses.color_pair(3) | curses.A_BOLD, splits_cords
        ) as splits_win:
            splits_win.set_bkgd(" ", curses.color_pair(3) | curses.A_BOLD)
            splits_win.add_win_label(
                "%.2d:%.2d /500m" % (pace_mins, pace_secs),
                curses.color_pair(3) | curses.A_BOLD,
            )
            splits_win.refresh()

        with Window(
            tm_caption, curses.color_pair(4) | curses.A_BOLD, tm_cords
        ) as tm_win:
            tm_win.set_bkgd(" ", curses.color_pair(4) | curses.A_BOLD)
            tm_win.add_win_label(
                "%.4d m" % (total_meters), curses.color_pair(4) | curses.A_BOLD
            )
            tm_win.refresh()

        with Window(
            hr_caption, curses.color_pair(5) | curses.A_BOLD, hr_cords
        ) as hr_win:
            hr_win.set_bkgd(" ", curses.color_pair(5) | curses.A_BOLD)
            hr_win.add_win_label(
                "%.3d bpm" % (hrate), curses.color_pair(5) | curses.A_BOLD
            )
            hr_win.refresh()

        plot_colours = [curses.color_pair(1), curses.color_pair(2), curses.color_pair(3)]
        with ForceCurve(
            Exit_Caption,
            curses.color_pair(6) | curses.A_BOLD,
            fc_cords,
            plot_colours,
        ) as fc_win:
            fc_win.set_bkgd(" ", curses.color_pair(6) | curses.A_BOLD)
            fc_win.add_win_label(
                "Force curve", curses.color_pair(6) | curses.A_BOLD
            )
            fc_win.refresh()
            fc_win._window.nodelay(True)

        # Main PM monitor loop; specify pressing 'q' to exit loop and
        # end execution.
        ch = 0
        while ch != ord("q"):
            ch = fc_win._window.getch()
            if ch < 0:
                ch = 0
            monitor = erg.get_monitor()

            total_meters = monitor["distance"]
            tm_win.update_label("%.4d m" % (total_meters))

            cals_hr = monitor["calhr"]  # pre processed data
            cals_hr = str(int(math.ceil(cals_hr)))

            # python math function to get mins and secs
            pace_mins, pace_secs = divmod(monitor["pace"], 60)
            splits_win.update_label("%.2d:%.2d /500m" % (pace_mins, pace_secs))

            wtime_mins, wtime_secs = divmod(monitor["time"], 60)
            tet_win.update_label("%.2d:%.2d" % (wtime_mins, wtime_secs))

            srate = monitor["spm"]
            spm_win.update_label("%.2d /spm" % (srate))

            hrate = monitor["heartrate"]
            hr_win.update_label("%.3d bpm" % (hrate))

            power = monitor["power"]

            if fc_win is not None:
                force = []
                force = erg.get_forceplot_data()
                if len(force) > 0:
                    fc_win.update_forcecurve(force)
                    fc_win.redraw()

    except Exception:
        caughtExceptions += format_exc()

    finally:
        # Debugging help.
        stdscr.addstr(0, 0, "Chosen layout is [" + chosenLayout + "]")
        stdscr.addstr(1, 10, f"{tet_caption} params are [{str(tet_cords)}]")
        stdscr.addstr(2, 10, f"{spm_caption} params are [{str(spm_cords)}]")
        stdscr.addstr(
            3, 10, f"{splits_caption} params are [{str(splits_cords)}]"
        )
        stdscr.addstr(4, 10, f"{tm_caption} params are [{str(tm_cords)}]")
        stdscr.addstr(5, 10, f"{hr_caption} params are [{str(hr_cords)}]")
        stdscr.addstr(6, 10, f"{fc_caption} params are [{str(fc_cords)}]")
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
    args = parse_options()
    if args is None:
        raise
        sys.exit(1)

    try:
        curses.wrapper(main)

    except Exception as err:
        print(str(err))
        print(format_exc())
        sys.exit(1)
