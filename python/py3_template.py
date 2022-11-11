#!/usr/bin/env python3
"""
Description:
"""
# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
# Standard
import sys
import os
import re
from time import sleep
from traceback import format_exc
from random import choice, randint, uniform
import ssl
import json
from datetime import datetime
from threading import Thread
from multiprocessing import Process
import requests
from netaddr import IPNetwork

# Third party
from nslookup import Nslookup

# local


# -----------------------------------------------------------------------------
#                           Global definitions
# -----------------------------------------------------------------------------
__author__ = "Copyright (c) 2022, W P Dulyea, All rights reserved."
__email__ = "wpdulyea@yahoo.com"
__version__ = "$Name: Release 0.1.0 $"[7:-2]


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
        ...

    except KeyboardInterrupt:
        print("Aborted the script execution through keyboard interrupt")
        sys.exit(0)
    except Exception as err:
        print(str(err))
        print(format_exc())
        sys.exit(1)
