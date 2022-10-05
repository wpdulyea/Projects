#!/usr/bin/env python3
__author__ = "William Dulyea"
__email__ = "wpdulyea@yahoo.com"

try:
    import sys
    import os
    from time import sleep
    from traceback import format_exc
    from random import choice
    import ssl
    from random import randint, uniform
    import json
    from datetime import datetime
    from threading import Thread
    from multiprocessing import Process
    from nslookup import Nslookup
    from argparse import ArgumentParser
    from copy import deepcopy
    from netaddr import IPNetwork
    import re
    import requests

except ImportError as err:
    print(f"Module import failed due to {err}")
    sys.exit(1)



def read_inputs():
    res = None
    try:
        parser = ArgumentParser()
        parser.add_argument("-a", help="Is for Apple", type=str, required=false)
        parser.add_argument(
            "-b", help="Is for how many Ballon(s)", type=int, required=True
        )
        res = parser.parse_args()
    except Exception as error:
        print(str(error))
    finally:
        return res


if __name__ == "__main__":

    cmd_name = os.path.splitext(os.path.basename(__file__))[0]
    args = read_inputs()
    if args is None:
        raise Exception
        sys.exit(1)

    try:
        ns = Nslookup()
        if args.a:
            print(f'Got agrs.a {args.a}')

        if args.b:
            print(f'Got args.b {args.b} is pseciofied')

    except KeyboardInterrupt:
        logger.error("Aborted the script execution through keyboard interrupt")
        sys.exit()
    except Exception as err:
        logger.error(str(err))
        print(format_exc())
        sys.exit()
