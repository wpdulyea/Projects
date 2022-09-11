#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Very simple HTTP server in python.

Example:
    %prog -p port-number (Starts the Server listening on specified port).
    %prog -s host/IPv4 (which defaults to localhost - us '' to listen on all addresses).
"""
# -----------------------------------------------------------------------------
#                               Imports
# -----------------------------------------------------------------------------
try:
    from http.server import SimpleHTTPRequestHandler, BaseHTTPRequestHandler, HTTPServer
    from multiprocessing import Process
    from socketserver import ForkingMixIn
    from socket import gethostbyname, gethostname
    from functools import partial
    from time import sleep
    import json
    import sys
    import cgi
except ImportError as err:
    print(f"Module import failed due to {err}")
    sys.exit(1)

# -----------------------------------------------------------------------------
#                               Global Data
# -----------------------------------------------------------------------------
__author__ = "William Dulyea"
__email__ = "wpdulyea@yahoo.com"

# -----------------------------------------------------------------------------
#                               Classes
# -----------------------------------------------------------------------------
class MPServer(ForkingMixIn, HTTPServer):
    pass


class PathRequestHandler(SimpleHTTPRequestHandler):
    pass


class RequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    ok_response_body = (
        "<html><body><h1>Hello!</h1><br><h3>How are you today?</h3></body></html>"
    )
    big_body = "lots and lots of useless text repeated - " * 8 * 4096

    def _print_hearders(self):
        print("Headers:")
        for name, value in sorted(self.headers.items()):
            print(f"{name}={value.rstrip()}")

    def _print_connection(self):

        print("Recieved From:")
        print(f"Client: {str(self.client_address)}")
        try:
            print(f'User-agent: {str(self.headers["user-agent"])}')
        except:
            pass
        print(f"Path: {self.path}\n")
        try:
            content_length = int(self.headers["content-length"])
            content_type = str(self.headers["content-type"])
            body = self.rfile.read(content_length)
            if body:
                print("Response body:\n")
                if "json" in content_type:
                    print(json.dumps(json.loads(body), indent=3, sort_keys=False))
                else:
                    print(f"{body}\n")
        except:
            pass

    def _set_headers(self, body=None):
        self.send_response(200)
        if body is not None:
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", len(body))

        self.end_headers()

    def do_GET(self):
        self._print_hearders()
        self._print_connection()

        self._set_headers(self.ok_response_body)
        self.wfile.write(self.ok_response_body.encode("utf-8"))
        return

    def do_POST(self):

        # Begin the response
        self._print_hearders()
        self._print_connection()
        self._set_headers(self.ok_response_body)
        self.wfile.write(self.ok_response_body)
        self.wfile.close()

        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers["Content-Type"],
            },
        )

        # Process the form contents if any
        if len(form):
            print("\nForm Data:")

            # Echo back information about what was posted in the form
            for field in form.keys():
                field_item = form[field]
                if field_item.filename:
                    # The field contains body data
                    file_data = field_item.file.read()
                    file_len = len(file_data)
                    del file_data
                    print(
                        f'RCVD {field} as "{field_item.filename}" File size:{file_len} bytes\n'
                    )
                else:
                    # Regular form value
                    print(f"{field}={form[field].value}\n")


# -----------------------------------------------------------------------------
#                               Functions
# -----------------------------------------------------------------------------
def read_args():
    args = None
    try:
        from argparse import ArgumentParser

        address = gethostbyname(gethostname())

        parser = ArgumentParser(usage=__doc__)
        parser.add_argument(
            "-p",
            dest="port",
            type=int,
            default=6050,
            help="Specifies the port number to listen on.",
        )
        parser.add_argument(
            "-s",
            dest="hostname",
            default=address,
            help="Specify the hostname or IPv4 address to listen on",
        )
        parser.add_argument(
            "-r",
            dest="rcode",
            type=int,
            default=200,
            help="Specify the HTTP response code to send to client",
        )
        parser.add_argument(
            "-d",
            dest="dir",
            type=str,
            default=None,
            help="Directory where the server will serve requested files from.",
        )
        args = parser.parse_args()
    except Exception as error:
        print(str(error))
    finally:
        return args


def main():

    options = read_args()
    if options is None:
        print("Failed to parse command line arguments")
        sys.exit(1)

    try:
        server_address = (options.hostname, options.port)
        if options.dir is not None:
            handler = partial(PathRequestHandler, directory=options.dir)
            # include a test for checking specified path as valid and readable
            httpd = MPServer(server_address, handler)
        else:
            httpd = MPServer(server_address, RequestHandler)

        parent = Process(target=httpd.serve_forever)
        parent.daemon = True

        print(f"Started HTTP service on Host {options.hostname} port {options.port}...")
        parent.start()
        parent.join()

    except KeyboardInterrupt:
        print("\nShutting Down Server....\n")
        parent.terminate()


# -----------------------------------------------------------------------------
#                               If run as main file
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    appName = os.path.splitext(os.path.basename(__file__))[0]
    print(f"\nRunning: {appName}\nAuthor: {__author__}\n")
    print(f"Contact {__email__} for any questions.\n")

    main()
