#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
Description:
    TCP Echo Service with delay.  If the message contains 'sleep n' when n is
    an integer value then the response will be delayed for n seconds.

Example:
    %prog -p port-number (Starts the Server listening on specified port).
    %prog -s hostname (which defaults to localhost).
"""
#-----------------------------------------------------------------------------
#                               Imports
#-----------------------------------------------------------------------------
from SocketServer import TCPServer
from multiprocessing import Process
from SocketServer import ForkingMixIn
from SocketServer import BaseRequestHandler
from time import sleep
import re
from os import curdir, sep
import sys
import json

#-----------------------------------------------------------------------------
#                           Global definitions
#-----------------------------------------------------------------------------
__author__  = "Copyright (c) 2016, Brocade LTD, All rights reserved."
__email__   = "wdulyea@brocade.com"
__version__ = "$Name: Release 0.1.0 $"[7:-2]

# Used by the email system to email reports to.
DEFAULT_EMAIL = __email__

#-----------------------------------------------------------------------------
#                         Class definitions
#-----------------------------------------------------------------------------
class TCPMessageHandler(BaseRequestHandler):
   MAX_MSG_SZ = 1024
   data = ''
   
   def handle(self):
      '''The if check is specific to transaction metadata which is new line
      terminated between records sent on long lived connections.'''
      while True:
         buf = self.request.recv(self.MAX_MSG_SZ)
         self.data += buf
         if '\n' in buf: break
           
      print "{} message:".format(self.client_address[0])
      self.parse_message()
      '''Echo the message back to sender'''
      self.request.sendall(self.data)

   def parse_message(self):
      s = re.compile('sleep\s+(\d+)')
      match = s.search(self.data)
      if match:
         value = int(match.group(1))

         print "Going delay echo for %i/sec\n" %value
         sleep(value)
      else:
         try:
            print( json.dumps(json.loads( self.data ), indent=3, sort_keys=False) )
         except:
            print self.data
            
class MPTCPServer( ForkingMixIn, TCPServer ):
   pass
#-----------------------------------------------------------------------------
#                         Function definitions
#-----------------------------------------------------------------------------
def main():
   from optparse import OptionParser

   appName = str(sys.argv[0]).split(sep).pop()
   print "\nRunning: %s, %s" %(appName,__version__)
   print "%s" %__author__
   print "Contact %s for any questions.\n" %__email__
   #
   #

   use = __doc__
   parser = OptionParser(usage=use)
   parser.add_option('-p', dest='port', type=int, default=6050,
      help='Specifies the port number to listen on.')
   parser.add_option('-s', dest='hostname', default='localhost',
      help='Specify the hostname or IPv4 address to listen on')
   (options, args) = parser.parse_args()

   # Start the Server on option.port-number
   try:
      server = MPTCPServer( (options.hostname, options.port), TCPMessageHandler )
      # Start a thread with the server -- that thread will then start one
      # more thread for each request
      worker = Process( target=server.serve_forever )
      # Exit the server thread when the main thread terminates
      worker.daemon = True

      print 'Started TCP Echo service on Host %s port %i...' %(options.hostname, options.port)
      worker.start()
      worker.join()

   except KeyboardInterrupt:
      print "\nShutting Down Server....\n"
      worker.terminate()

#-----------------------------------------------------------------------------
#                            Main Entry point
#-----------------------------------------------------------------------------
if __name__ == '__main__':
      ret = main()
      sys.exit(ret)
