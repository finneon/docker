#!/usr/bin/env python
# Testing remote function using xmlrpc
from xmlrpc.server import SimpleXMLRPCServer
import logging
import socket


ECHO_PORT = 11881
host_name = socket.gethostname()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

server = SimpleXMLRPCServer(('', ECHO_PORT), logRequests=True)
logging.debug("Server listening at host %s with port %d",
              host_name, ECHO_PORT)


# Expose a function
def echo(text):
    logging.debug("processing echo(%s)", text)
    return "%s: %s" % (host_name, text)


server.register_function(echo)


try:
    print("Use Control-C to exit")
    server.serve_forever()
except KeyboardInterrupt:
    print("Exiting")
