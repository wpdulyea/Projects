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

# -----------------------------------------------------------------------------
#                           Global definitions
# -----------------------------------------------------------------------------
__author__ = "Copyright (c) 2022, W P Dulyea, All rights reserved."
__email__ = "wpdulyea@yahoo.com"
__version__ = "$Name: Release 0.1.0 $"[7:-2]

layouts = [
    "2 top, 1 bottom",
    "2 left, 1 right",
    "1 top, 2 bottom",
    "1 left, 2 right",
]

# -----------------------------------------------------------------------------
#                               Classes
# -----------------------------------------------------------------------------


class MainWindow(object):
    bgColors = [
        curses.COLOR_BLUE,
        curses.COLOR_CYAN,
        curses.COLOR_GREEN,
        curses.COLOR_MAGENTA,
        curses.COLOR_RED,
        curses.COLOR_YELLOW,
    ]

    def __init__(self):
        # Initialize the curses object.
        self.scr = curses.initscr()
        self.scr.refresh()
        self.scr.box()

        # Do not echo keys back to the client.
        curses.noecho()

        # Non-blocking or cbreak mode... do not wait for Enter key to be pressed.
        curses.cbreak()

        # Turn off blinking cursor
        curses.curs_set(False)

        # Enable color if we can...
        if curses.has_colors():
            curses.start_color()

        # Optional - Enable the keypad. This also decodes multi-byte key sequences
        self.scr.keypad(True)
        self.colors = sample(self.bgColors, 3)


class Window(object):
    """
    Base class for a subwindow.
    """

    def __init__(
        self, caption: str, attr: int, h: int, w: int, x: int, y: int
    ):

        self.caption = caption
        self.capt_attr = attr
        self.width = w
        self.height = h
        self.y_pos = y
        self.x_pos = x
        try:

            self.window = curses.newwin(h, w, y, x)
            self.window.box()
            if "" != caption:
                # The "Y coordinate" here is the bottom of the *window* and not the screen.
                self.window.addstr(
                    self.height - 2,
                    1,
                    str(caption),
                    self.capt_attr,
                )
            self.window.refresh()
        except Exception as err:
            raise err

    def set_bkgd(self, ch, attr=0):
        self.window.bkgd(ch, attr)

    def add_win_label(self, label: str, attr: int):
        """
        Add the string to the center, with BOLD flavoring.
        """
        # Calculate rough center
        self.window.addstr(
            self.height // 2,
            (self.width // 2) - 4,
            str(label),
            attr,
        )

    def redraw(self):
        self.window.refresh()

    def get_char(self):
        self.window.getch()


# -----------------------------------------------------------------------------
#                               Functions
# -----------------------------------------------------------------------------
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
    # Initialize the curses object.
    stdscr = curses.initscr()
    stdscr.refresh()
    stdscr.box()

    # Do not echo keys back to the client.
    curses.noecho()

    # Non-blocking or cbreak mode... do not wait for Enter key to be pressed.
    curses.cbreak()

    # Turn off blinking cursor
    curses.curs_set(False)

    # Enable color if we can...
    if curses.has_colors():
        curses.start_color()

    # Optional - Enable the keypad. This also decodes multi-byte key sequences
    stdscr.keypad(True)

    # Beginning of Program...
    # Create a list of all the colors except for black and white. These will
    # server as the background colors for the windows. Because these constants
    # are defined in ncurses,
    # we can't create the list until after the curses.initscr call:
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
    colors = sample(bgColors, 6)

    # Create ncurses color pair objects.
    curses.init_pair(1, curses.COLOR_WHITE, colors[0])
    curses.init_pair(2, curses.COLOR_WHITE, colors[1])
    curses.init_pair(3, curses.COLOR_WHITE, colors[2])
    curses.init_pair(4, curses.COLOR_WHITE, colors[3])
    curses.init_pair(5, curses.COLOR_WHITE, colors[4])
    curses.init_pair(6, curses.COLOR_WHITE, colors[5])

    caughtExceptions = ""
    Monitor = {}
    try:

        # The lists below will eventually hold 4 values, the X and Y
        # coordinates of the  top-left corner relative to the screen itself
        # and the number of characters going right and down, respectively.
        window1 = []
        window2 = []
        window3 = []
        window4 = []
        window5 = []
        window6 = []

        # The variables below will eventually contain the window objects.
        window1Obj = None
        window2Obj = None
        window3Obj = None
        window4Obj = None
        window5Obj = None
        window6Obj = None

        # There's going to be a caption at the bottom left of the screen but it
        # needs to go in the proper window.
        window1Caption = ""
        window2Caption = ""
        window3Caption = ""
        window4Caption = ""
        window5Caption = ""
        window6Caption = ""

        # The randomly sized windows that don't take up one side of the screen
        # shouldn't be less than 1/3 the screen size, or more than one third of
        # the screen size on either edge.
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
        chosenLayout = layouts[0]  # [randrange(0, 4)]
        match chosenLayout:
            case "2 top, 1 bottom":
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
                    minWindowHeight * 4,
                ]

                window6Caption = chosenLayout + " - Press a key to quit."
            case "2 left, 1 right":
                # Windows 1 and 2 will be on the left, Window 3 will be on the right.
                window1Width = randrange(minWindowWidth, maxWindowWidth)
                window1Height = randrange(minWindowHeight, maxWindowHeight)
                window1 = [0, 0, window1Width, window1Height]

                window2Width = window1Width
                window2Height = curses.LINES - window1Height
                window2 = [0, window1Height, window2Width, window2Height]
                window2Caption = chosenLayout + " - Press a key to quit."

                window3Width = curses.COLS - window1Width
                window3Height = curses.LINES
                window3 = [window1Width, 0, window3Width, window3Height]
            case "1 top, 2 bottom":
                # Window 1 will be on the top, Windows 2 and 3 will be on the bottom.
                window1Width = curses.COLS
                window1Height = randrange(minWindowHeight, maxWindowHeight)
                window1 = [0, 0, window1Width, window1Height]

                window2Width = randrange(minWindowWidth, maxWindowWidth)
                window2Height = curses.LINES - window1Height
                window2 = [0, window1Height, window2Width, window2Height]
                window2Caption = chosenLayout + " - Press a key to quit."

                window3Width = curses.COLS - window2Width
                window3Height = window2Height
                window3 = [
                    window2Width,
                    window1Height,
                    window3Width,
                    window3Height,
                ]
            case "1 left, 2 right":
                # Window 1 will be on the left, Windows 2 and 3 will be on the right.
                window1Width = randrange(minWindowWidth, maxWindowWidth)
                window1Height = curses.LINES
                window1 = [0, 0, window1Width, window1Height]
                window1Caption = chosenLayout + " - Press a key to quit."

                window2Width = curses.COLS - window1Width
                window2Height = randrange(minWindowHeight, maxWindowHeight)
                window2 = [window1Width, 0, window2Width, window2Height]

                window3Width = window2Width
                window3Height = curses.LINES - window2Height
                window3 = [
                    window1Width,
                    window2Height,
                    window3Width,
                    window3Height,
                ]
            case _:
                raise Exception("oops!, no mtching case")

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
            "Window 1", curses.color_pair(1) | curses.A_BOLD
        )
        window1Obj.redraw()

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
            "Window 2", curses.color_pair(2) | curses.A_BOLD
        )
        window2Obj.redraw()

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
            "Window 3", curses.color_pair(3) | curses.A_BOLD
        )
        window3Obj.redraw()

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
            "Window 4", curses.color_pair(4) | curses.A_BOLD
        )
        window4Obj.redraw()

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
            "Window 5", curses.color_pair(5) | curses.A_BOLD
        )
        window5Obj.redraw()

        window6Obj = Window(
            window6Caption,
            curses.color_pair(6) | curses.A_BOLD,
            window6[3],
            window6[2],
            window6[1],
            window6[0],
        )
        window6Obj.set_bkgd(" ", curses.color_pair(6) | curses.A_BOLD)
        window6Obj.add_win_label(
            "Window 6", curses.color_pair(6) | curses.A_BOLD
        )
        window6Obj.redraw()

        # Necessary so we can "pause" on the window output before quitting.
        window6Obj.get_char()

        # Debugging output.
        stdscr.addstr(0, 0, "Chosen layout is [" + chosenLayout + "]")
        stdscr.addstr(1, 10, "Window 1 params are [" + str(window1) + "]")
        stdscr.addstr(2, 10, "Window 2 params are [" + str(window2) + "]")
        stdscr.addstr(3, 10, "Window 3 params are [" + str(window3) + "]")
        stdscr.addstr(4, 10, "Colors are [" + str(colors) + "]")
        stdscr.addstr(5, 0, "Press a key to continue.")
        stdscr.refresh()
        stdscr.getch()
    except Exception as err:
        caughtExceptions = str(err)

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
