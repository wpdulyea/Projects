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
           H,   W,   y,   x                        H,   W,   y,   x
        ---------------------                    --------------------
    TET  = 1/7, 2/3, 0,   0               APACE  = 4/7, 0,  1/7,  3/3
    SPM  = 1/7, 1/3, 0,   2/3             SM     = 5/7, 0,  1/7,  3/3
    PACE = 2/7, 3/3, 1/7, 0               PFM    = 6/7, 0,  2/7,  3/3
    TM   = 1/7, 2/3, 3/7, 0
    HR   = 1/7, 1/3, 3/7, 2/3
    PLOT = 3/7, 3/3, 4/7, 0
"""

# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
# Standard
import sys
import os
import math
from traceback import format_exc
from random import sample
import curses
from curses import ascii

# Local packages
from pyrowlib import pyrow
from pyrowlib import csafe_dic

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
    Base class for a curses subwindow specialized to contain a PM monitor
    display panel.

    :param str caption: String to disply at the top-left of Window
    :param int attr: String attributes for addstr()
    :param list cords: List containing the [y-axis, x-axis, height, width]
    :return: Window Object
    """

    def __init__(
        self: object, pwin: object, caption: str, attr: int, cords: list
    ):
        self._caption = caption
        self._attr = attr
        self._cords = cords

        self._window = pwin.derwin(*cords)
        if "" != caption:
            self._add_caption()

        self._window.refresh()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    @property
    def coordinates(self):
        return self._cords

    @coordinates.setter
    def coordinates(self, value: list[int]):
        self._cords = value

    @proprty
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, caption: str = None, attr: int = None):
        if caption is None:
            self._add_caption()
        elif attr is not None:
            self._attr = attr
        self._add_caption()

    def _add_caption(self):
        """
        Position the optional caption to the upper left corner 1x1.
        """
        self._window.box()
        self._window.addstr(
            0,
            1,
            str(self._caption),
            self._attr,
        )

    def _add_label(self):
        """
        Add dispayed label = formatted string
        to the calculate rough center of window.
        """
        max_y, max_x = self._window.getmaxyx()
        self._window.addstr(
            max_y // 2,
            (max_x - len(self._label)) // 2,
            str(self._label),
            self._label_attr,
        )

    def set_bkgd(self, attr: int = None):
        if attr is not None:
            self._attr = attr

        self._window.bkgd(" ", self._attr)
        self._window.bkgdset(" ", self._attr)

    def add_win_label(self, label: str, attr: int):
        """
        Add formatted string and attribute and then call internal
        _add_label() to paint to window.
        """
        self._label = label
        self._label_attr = attr

        self._add_label()

    def update_label(self: object, label: str):
        """
        Update formatted string and redraw to window.
        """
        self._label = label
        self._add_label()
        self.refresh()

    def redraw(self, cords: list = None):
        """
        Redraws this window object based on the objects current state.
        """

        self._window.clear()
        if cords is not None:
            self._cords = cords
            self._window.mvderwin(self._cords[2], self._cords[3])
            self._window.mvwin(self._cords[2], self._cords[3])
            self._window.resize(self._cords[0], self._cords[1])
            self._window.redrawwin()

        self._window.box()
        self._add_caption()
        self._add_label()
        self.set_bkgd()
        # Might need to add some code to repaint the window on terminal
        # resize if supported.
        self.refresh()

    def refresh(self):
        self._window.refresh()


class ForceCurve(Window):
    """
    sub class of Window specialised to create and update PM Monitor
    forcecurve data. The plotColours list will determine the number
    of force curves to keep record of, one for each colour in the
    list.

    :param str caption: see parent for details
    :param int attr: see parent for details
    :param list cords: see parent for details
    :param list plotColours: List of curses initialised color objects.
    :return: Window Object
    """

    # Character used to represent the plot points.
    _pchar = "-"
    # power reading.
    _power = []

    # Record each plot up to len of pColours. Once len of each is == then clean
    # lastPlot [] = forcecurve data list
    _lastPlot = []

    def __init__(
        self: object,
        pwin: object,
        caption: str,
        attr: int,
        cords: list,
        plotColours: list,
    ):
        super().__init__(pwin, caption, attr, cords)
        self._pColours = plotColours

    def update_forcecurve(self, data: list = None, power: int = None):
        """
        Given a forcecuve data list, and power val:
            print the power (in Watts) and plot the force curve from data list.
        :param list data: forcecurve int list, up to size=16.
        :param int power: int value in max watts for this stroke.
        """
        y_max, x_max = self._window.getmaxyx()
        y_min, x_min = self._window.getbegyx()
        y_max -= 2
        x_max -= 2
        # Start Y axis at + 2 to avoid overlap with box line.
        y_plot = y_min - 2
        # Start X axis at 1/4 of the width of the given window.
        x_plot = x_max * 1 // 8
        # x axis step to next start of plot
        x_step = (x_max - x_plot) * 1 // 2

        # ToDo: It is not clear where this value comes from.
        max_force = 300
        if y_max < max_force:
            y_scaled = y_max / max_force
        else:
            y_scaled = 1

        # If there is no data re-plot current contents - usually on a redraw.
        if data is not None:
            if len(self._lastPlot) >= len(self._pColours):
                self._lastPlot = []
                self._power = []

            self._lastPlot.append(data)
            self._power.append(power)

        yp = 4
        for p in range(len(self._lastPlot)):
            # Start Y axis at + 2 to avoid overlap with box line.
            y_plot = y_min - 2
            # Start X axis at 1/4 of the width of the given window.
            x_plot = x_max * 1 // 8
            # x axis step to next start of plot
            x_step = 1
            # Power label
            self._window.addstr((yp + p), 2, "Max Power:%.2i Watts" % (self._power[p]), self._pColours[p])
            for d in self._lastPlot[p]:
                y_plot = y_max - math.floor(d * y_scaled)
                # Check that x/y-axis limits are not exceeded.
                if y_plot > y_max:
                    y_plot = y_max
                if x_plot > x_max:
                    x_plot = x_max
                self._window.addstr(y_plot, x_plot, self._pchar, self._pColours[p])
                x_plot += x_step

        self.refresh()

        def redraw(self: object, cords: int = None):
            super().redraw(cords)
            self.update_forcecurve()


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
            "--menu",
            help="With PM menu - (not implemented)",
            action="store_true",
            required=False,
        )
        parser.add_argument(
            "--standard",
            help="Current workout data",
            action="store_true",
            required=False,
        )
        parser.add_argument(
            "--with-force-curve",
            help="Add the force curve plot window",
            action="store_true",
            required=False,
        )
        res = parser.parse_args()
    except Exception as error:
        print(str(error))
    finally:
        return res


def main(stdscr):
    # Initialize the curses.
    stdscr = curses.initscr()

    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    stdscr.keypad(False)

    if curses.has_colors():
        curses.start_color()

    Colours = [
        [curses.COLOR_BLUE, curses.COLOR_YELLOW],
        [curses.COLOR_CYAN, curses.COLOR_MAGENTA],
        [curses.COLOR_GREEN, curses.COLOR_RED],
        [curses.COLOR_MAGENTA, curses.COLOR_CYAN],
        [curses.COLOR_RED, curses.COLOR_GREEN],
        [curses.COLOR_YELLOW, curses.COLOR_BLUE],
        [curses.COLOR_BLACK, curses.COLOR_WHITE],
    ]
    # Random selection of colours
    colours = sample(Colours, 6)

    # Curses colours.
    curses.init_pair(1, colours[0][0], colours[0][1])
    curses.init_pair(2, colours[1][0], colours[1][1])
    curses.init_pair(3, colours[2][0], colours[2][1])
    curses.init_pair(4, colours[3][0], colours[3][1])
    curses.init_pair(5, colours[4][0], colours[4][1])
    curses.init_pair(6, colours[5][0], colours[5][1])

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
        erg = conn2erg(stdscr)
        if erg is None:
            raise Exception("Failed to connect with erg")

        # Window dimensions will be proportinally based
        # as illustgrated in top of file.
        #        H,   W,   y,   x
        #       ------------------
        # TET  = 1/7, 2/3, 0,   0
        # SPM  = 1/7, 1/3, 0,   2/3
        # PACE = 2/7, 3/3, 1/7, 0
        # TM   = 1/7, 2/3, 3/7, 0
        # HR   = 1/7, 1/3, 3/7, 2/3
        # PLOT = 3/7, 3/3, 4/7, 0
        minWidth = curses.COLS * 1 // 3
        maxWidth = curses.COLS - minWidth
        minHeight = curses.LINES * 1 // 7
        maxHeight = 2 * minHeight

        # Select a layout.
        chosenLayout = layouts[0]
        match chosenLayout:
            case "Standard with force curve":
                # Windows [height, width, y, x]
                tet_cords = [minHeight, maxWidth, 0, 0]
                spm_cords = [minHeight, minWidth, 0, tet_cords[1]]
                splits_cords = [
                    maxHeight,
                    curses.COLS,
                    tet_cords[0],
                    0,
                ]
                tm_cords = [
                    minHeight,
                    maxWidth,
                    tet_cords[0] + splits_cords[0],
                    0,
                ]
                hr_cords = [
                    minHeight,
                    minWidth,
                    tm_cords[2],
                    tm_cords[1],
                ]
                fc_cords = [
                    curses.LINES
                    - (tet_cords[0] + splits_cords[0] + tm_cords[0]),
                    curses.COLS,
                    tet_cords[0] + splits_cords[0] + tm_cords[0],
                    0,
                ]

                Exit_Caption = chosenLayout + "Press 'ESC' key to quit."
            case _:
                raise Exception("oops!, no matching case")

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
            stdscr,
            tet_caption,
            curses.color_pair(1) | curses.A_BOLD,
            tet_cords,
        ) as tet_win:
            tet_win.set_bkgd(curses.color_pair(1) | curses.A_BOLD)
            tet_win.add_win_label(
                "%.2d:%.2d" % (wtime_mins, wtime_secs),
                curses.color_pair(1) | curses.A_BOLD,
            )
            tet_win.refresh()

        with Window(
            stdscr,
            spm_caption,
            curses.color_pair(2) | curses.A_BOLD,
            spm_cords,
        ) as spm_win:
            spm_win.set_bkgd(curses.color_pair(2) | curses.A_BOLD)
            spm_win.add_win_label(
                "%.2d /spm" % (srate), curses.color_pair(2) | curses.A_BOLD
            )
            spm_win.refresh()

        with Window(
            stdscr,
            splits_caption,
            curses.color_pair(3) | curses.A_BOLD,
            splits_cords,
        ) as splits_win:
            splits_win.set_bkgd(curses.color_pair(3) | curses.A_BOLD)
            splits_win.add_win_label(
                "%.2d:%.2d /500m" % (pace_mins, pace_secs),
                curses.color_pair(3) | curses.A_BOLD,
            )
            splits_win.refresh()

        with Window(
            stdscr, tm_caption, curses.color_pair(4) | curses.A_BOLD, tm_cords
        ) as tm_win:
            tm_win.set_bkgd(curses.color_pair(4) | curses.A_BOLD)
            tm_win.add_win_label(
                "%.4d m" % (total_meters), curses.color_pair(4) | curses.A_BOLD
            )
            tm_win.refresh()

        with Window(
            stdscr, hr_caption, curses.color_pair(5) | curses.A_BOLD, hr_cords
        ) as hr_win:
            hr_win.set_bkgd(curses.color_pair(5) | curses.A_BOLD)
            hr_win.add_win_label(
                "%.3d bpm" % (hrate), curses.color_pair(5) | curses.A_BOLD
            )
            hr_win.refresh()

        plot_colours = [
            curses.color_pair(1),
            curses.color_pair(2),
            curses.color_pair(3),
        ]
        with ForceCurve(
            stdscr,
            f"{fc_caption} - {Exit_Caption}",
            curses.color_pair(6) | curses.A_BOLD,
            fc_cords,
            plot_colours,
        ) as fc_win:
            fc_win.set_bkgd(curses.color_pair(6) | curses.A_BOLD)
            fc_win.add_win_label(
                "Force curve", curses.color_pair(6) | curses.A_BOLD
            )
            fc_win.refresh()

        # Main PM monitor loop; specify pressing 'q' to exit loop and
        # end execution.
        stdscr.nodelay(True)
        State = csafe_dic.STATE_MACHINE_STATE
        ch = 0
        max_y, max_x = stdscr.getmaxyx()
        while True:
            ch = stdscr.getch()
            if ch == ascii.ESC:
                break
            if ch == -1:
                ch = 0
            if ch == curses.KEY_RESIZE:
                stdscr.clear()
                if curses.is_term_resized(max_y, max_x):
                    curses.update_lines_cols()
                    max_y, max_x = stdscr.getmaxyx()
                    min_y, min_x = stdscr.getbegyx()
                    curses.resizeterm(max_y, max_x)

                    minWidth = max_x * 1 // 3
                    maxWidth = max_x - minWidth
                    minHeight = max_y * 1 // 7
                    maxHeight = 2 * minHeight
                    tet_cords = [minHeight, maxWidth, min_y, min_x]
                    spm_cords = [minHeight, minWidth, min_y, tet_cords[1]]
                    splits_cords = [minHeight * 2, curses.COLS, tet_cords[0], min_x]
                    tm_cords = [
                        minHeight,
                        maxWidth,
                        tet_cords[0] + splits_cords[0],
                        min_x,
                    ]
                    hr_cords = [minHeight, minWidth, tm_cords[2], tm_cords[1]]
                    fc_cords = [
                        max_y - (tet_cords[0] + splits_cords[0] + tm_cords[0]),
                        max_x, tet_cords[0] + splits_cords[0] + tm_cords[0], 0]
                    tet_win.redraw(tet_cords)
                    spm_win.redraw(spm_cords)
                    splits_win.redraw(splits_cords)
                    tm_win.redraw(tm_cords)
                    hr_win.redraw(hr_cords)
                    fc_win.redraw(fc_cords)

                stdscr.refresh()
                stdscr.getch()

            monitor = erg.get_monitor()

            match monitor['status']:
                case State.IN_USE:
                    pass
                case State.MANUAL:
                    pass
                case State.READY:
                    pass
                case _:
                    #print(f'Reported status:{hex(monitor["status"])}')
                    pass

            total_meters = monitor["distance"]
            cals_hr = monitor["calhr"]  # pre processed data
            # python math function to get mins and secs
            pace_mins, pace_secs = divmod(monitor["pace"], 60)
            wtime_mins, wtime_secs = divmod(monitor["time"], 60)
            srate = monitor["spm"]
            hrate = monitor["heartrate"]
            cals_hr = str(int(math.ceil(cals_hr)))

            tm_win.update_label("%.4d m" % (total_meters))
            splits_win.update_label("%.2d:%.2d /500m" % (pace_mins, pace_secs))
            tet_win.update_label("%.2d:%.2d" % (wtime_mins, wtime_secs))
            spm_win.update_label("%.2d /spm" % (srate))
            hr_win.update_label("%.3d bpm" % (hrate))

            force = []
            force = erg.get_forceplot_data()
            if len(force) > 0:
                power = monitor["power"]
                fc_win.update_forcecurve(force, power)

    except Exception:
        caughtExceptions += format_exc()

    finally:
        stdscr.erase()
        stdscr.box()
        stdscr.addstr(8, 0, "Press a key to continue.")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()

        curses.nocbreak()
        curses.echo()
        curses.curs_set(True)
        curses.endwin()

        # Print any Errors
        if "" != caughtExceptions:
            print(f"{caughtExceptions}")
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
