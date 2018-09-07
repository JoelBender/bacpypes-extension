#!/usr/bin/env python

"""
UDP Server
"""

import os

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ArgumentParser

from bacpypes.core import run, stop
from bacpypes.comm import Client, bind
from bacpypes.udp import UDPDirector

from custom import Custom

# some debugging
_debug = 0
_log = ModuleLogger(globals())

# settings
SERVER_HOST = os.getenv('SERVER_HOST', 'any')
SERVER_PORT = int(os.getenv('SERVER_PORT', 9000))

#
#   CustomClient
#

@bacpypes_debugging
class CustomClient(Custom, Client):

    def __init__(self):
        if _debug: CustomClient._debug("__init__")

#
#   __main__
#

def main():
    # parse the command line arguments
    parser = ArgumentParser(usage=__doc__)
    parser.add_argument(
        "host", nargs='?',
        help="listening address of server or 'any' (default %r)" % (SERVER_HOST,),
        default=SERVER_HOST,
        )
    parser.add_argument(
        "port", nargs='?', type=int,
        help="server port (default %r)" % (SERVER_PORT,),
        default=SERVER_PORT,
        )

    args = parser.parse_args()

    if _debug: _log.debug("initialization")
    if _debug: _log.debug("    - args: %r", args)

    host = args.host
    if host == "any":
        host = ''
    server_address = (host, args.port)
    if _debug: _log.debug("    - server_address: %r", server_address)

    udp_director = UDPDirector(server_address)
    bind(CustomClient(), udp_director)

    _log.debug("running")

    run()

    _log.debug("fini")

if __name__ == "__main__":
    main()
