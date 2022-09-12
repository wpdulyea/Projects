#!/usr/bin/env python3
"""
Description:
    TCP Echo Service with delay.  If the message contains 'sleep n' when n is
    an integer value then the response will be delayed for n seconds.

Example:
    %prog -p port-number (Starts the Server listening on specified port).
    %prog -s hostname (which defaults to localhost).
"""
# -----------------------------------------------------------------------------
#                               Imports
# -----------------------------------------------------------------------------
try:
    from socketserver import TCPServer, ForkingMixIn, BaseRequestHandler
    from socket import gethostbyname, gethostname
    from multiprocessing import Process
    from traceback import format_exc
    from time import sleep
    from os import curdir, sep
    import re
    import json
    import sys
except ImportError as err:
    print(f"Module import failed due to {err}")
    sys.exit(1)


# -----------------------------------------------------------------------------
#                           Global definitions
# -----------------------------------------------------------------------------
__author__ = "Copyright (c) 2022, W P Dulyea, All rights reserved."
__version__ = "$Name: Release 0.1.0 $"[7:-2]
__email__ = "wpdulyea@yahoo.com"

# -----------------------------------------------------------------------------
#                         Class definitions
# -----------------------------------------------------------------------------
class TCPMessageHandler(BaseRequestHandler):
    MAX_MSG_SZ = 1024
    regex = re.compile(r"sleep(\s+)(\d+)")
    data = ""

    def handle(self):
        """The if check is specific to transaction metadata which is new line
        terminated between records sent on long lived connections."""
        try:
            while True:
                buf = self.request.recv(self.MAX_MSG_SZ).decode('utf-8')
                if buf is None:
                    continue
                self.data += buf
                if "\n" in buf:
                    break

            print(f"{self.client_address[0]} message:")
            self.parse_message()
            """Echo the message back to sender"""
            self.request.sendall(bytes(self.data, "utf-8"))
        except Exception as error:
            print(str(error))

    def parse_message(self):
        try:
            match = self.regex.search(self.data)
            if match is not None:
                value = int(match.group(1))

                while 0 < value:
                    print("Response will be delayed for {value}/sec\n")
                    sleep(value)
                    value -= 1
            else:
                print(json.dumps(json.loads(self.data), indent=3, sort_keys=False))
        except json.JSONDecodeError:
            print(f"{self.data}")
        except Exception as error:
            print(str(error))


class MPTCPServer(ForkingMixIn, TCPServer):
    pass


# -----------------------------------------------------------------------------
#                         Function definitions
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
    worker = None
    server = None

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

        server = MPTCPServer((args.bind_address, args.port), TCPMessageHandler)
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        worker = Process(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        worker.daemon = True

        print(f"Started TCP echo service on Host {hostname} port {args.port}...")

        worker.start()
        worker.join()

    except KeyboardInterrupt:
        print("\nShutting Down Server....\n")
    except Exception as errmsg:
        ret = 1
        print(str(errmsg))
    finally:
        if worker is not None:
            worker.terminate()


# -----------------------------------------------------------------------------
#                            Main Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
