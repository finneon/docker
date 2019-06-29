#!/usr/bin/env python
# Test remote function using xmlrpc
# Usage: echo_client.py <echo_server_ip> <text>
import sys
import xmlrpc.client

ECHO_PORT = 11881

if len(sys.argv) != 3:
    print("Usage: echo_client <echo_server_ip> <text>")
    exit(1)

echo_server = xmlrpc.client.ServerProxy("http://%s:%d" % (sys.argv[1], ECHO_PORT))
print(echo_server.echo(sys.argv[2]))
