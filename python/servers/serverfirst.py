#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description:
    TCP Echo Service with delay.  If the message contains 'sleep n' when n is
    an integer value then the response will be delayed for n seconds.
    
Example:
    %prog -p port-number (Starts the Server listening on specified port).
    %prog -b bind-address (Host name IP address or default to bind to all interfaces).
"""
# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
try:
    from socketserver import TCPServer, BaseRequestHandler
    from socket import gethostbyname, gethostname
    from multiprocessing import Process
    from socketserver import ForkingMixIn
    from traceback import format_exc
    from time import sleep
    from os import curdir, sep
    import re
    import sys
except ImportError as err:
    print(f"Module import failed due to {err}")
    sys.exit(1)

# -----------------------------------------------------------------------------
#                           Global definitions
# -----------------------------------------------------------------------------
__author__ = "Copyright (c) 2022, W P Dulyea, All rights reserved."
__email__ = "wpdulyea@yahoo.com"
__version__ = "$Name: Release 0.1.0 $"[7:-2]

# -----------------------------------------------------------------------------
#                         Class definitions
# -----------------------------------------------------------------------------
class ServerFirst(TCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        TCPServer.__init__(self, server_address, RequestHandlerClass)

    def verify_request(self, request, client_address):
        print("Connected from ", client_address[0])
        if request:
            request.sendall(b"RDY_TOECHO\n")
            return True
        else:
            return False


class MPServer(ForkingMixIn, ServerFirst):
    pass


class MessageHandler(BaseRequestHandler):
    MAX_MSG_SZ = 1024
    regex = re.compile(r"sleep\s+(\d+)")
    shutdown = re.compile("shutdown")

    def handle(self):
        self.data = self.request.recv(self.MAX_MSG_SZ).strip()
        self.parse_message()
        print(f"{self.client_address[0]} wrote: {self.data}")
        self.request.sendall(bytes(self.data + "\n", "utf-8"))

    def parse_message(self):
        match = self.regex.search(str(self.data))
        if match is not None:
            value = int(match.group(1))
            while value > 0:
                self.request.sendall(
                    bytes("Response will be delayed for {value}/sec\n", "utf-8")
                )
                sleep(value)
                value -= 1


# -----------------------------------------------------------------------------
#                               Functions
# -----------------------------------------------------------------------------
def read_args():
    from argparse import ArgumentParser

    use = __doc__
    args = None

    try:
        parser = ArgumentParser(usage=use)
        parser.add_argument(
            "-p",
            dest="port",
            type=int,
            default=6050,
            help="Specifies the port number to listen on.",
        )
        parser.add_argument(
            "-b",
            dest="bind_address",
            default="",
            help="Hostname or IPv4 address to listen on - defaults to all interfaces",
        )
        args = parser.parse_args()

    except Exception as error:
        print(str(error))
    finally:
        return args


def main():

    ret = 0
    appName = str(sys.argv[0]).split(sep).pop()
    hostname = gethostname()

    print(f"\nRunning: {appName} {__version__}")
    print(f"{__author__}")
    print(f"Contact {__email__} for any questions.\n")
    #
    #
    try:
        args = read_args()
        if args is None:
            ret = 1
            raise Exception("Failed to parse command line arguments")

        # Start the Server on option.port-number
        servers = MPServer((args.bind_address, args.port), MessageHandler)
        parent = Process(target=servers.serve_forever)
        parent.daemon = True
        print(f"Host {hostname} listening on port {args.port}")
        print("Waiting to echo inbound messages")
        parent.start()
        parent.join()
    except KeyboardInterrupt:
        print("\nShutting Down Server....\n")
    except Exception as errmsg:
        print(str(errmsg))
    finally:
        if servers.socket is not None:
            servers.socket.close()
        return ret


# -----------------------------------------------------------------------------
#                            Main Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
