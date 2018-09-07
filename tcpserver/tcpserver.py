#!/usr/bin/env python

"""
This simple TCP server application listens for one or more client connections
and echos the incoming lines back to the client.  There is no conversion from
incoming streams of content into a line or any other higher-layer concept
of a packet.
"""

import os

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ArgumentParser

from bacpypes.core import run
from bacpypes.comm import PDU, Client, bind, ApplicationServiceElement
from bacpypes.tcp import TCPServerDirector, TCPServerActor

from custom import Custom

# some debugging
_debug = 0
_log = ModuleLogger(globals())

# settings
SERVER_HOST = os.getenv('SERVER_HOST', 'any')
SERVER_PORT = int(os.getenv('SERVER_PORT', 9000))
IDLE_TIMEOUT = int(os.getenv('IDLE_TIMEOUT', 0)) or None

# globals
args = None

#
#   CustomActor
#

@bacpypes_debugging
class CustomActor(Custom, TCPServerActor):

    def __init__(self, director, sock, peer):
        if _debug: CustomActor._debug("__init__ %r %r %r", director, sock, peer)
        TCPServerActor.__init__(self, director, sock, peer)
        Custom.__init__(self)

    def indication(self, pdu):
        """
        This function is normally called by the TCPServerDirector when it
        receives an indication from higher levels in the protocol stack.
        """
        if _debug: CustomActor._debug("indication %r", pdu)

        # continue as usual
        super(CustomActor, self).indication(pdu)

#
#   CustomASE
#

@bacpypes_debugging
class CustomASE(ApplicationServiceElement):
    """
    An instance of this class is bound to the director, which is a
    ServiceAccessPoint.  It receives notifications of new actors connected
    from a client, actors that are going away when the connections are closed,
    and socket errors.
    """
    def indication(self, add_actor=None, del_actor=None, actor_error=None, error=None):
        global args

        if add_actor:
            if _debug: CustomASE._debug("indication add_actor=%r", add_actor)

            # it's connected, maybe say hello
            if args.hello:
                add_actor.indication(PDU(b'Hello, world!\n'))

        if del_actor:
            if _debug: CustomASE._debug("indication del_actor=%r", del_actor)

        if actor_error:
            if _debug: CustomASE._debug("indication actor_error=%r error=%r", actor_error, error)

#
#   __main__
#

def main():
    global args

    # parse the command line arguments
    parser = ArgumentParser(description=__doc__)
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
    parser.add_argument(
        "--idle-timeout", nargs='?', type=int,
        help="idle connection timeout",
        default=IDLE_TIMEOUT,
        )
    parser.add_argument(
        "--hello", action="store_true",
        default=False,
        help="send a hello message to a client when it connects",
        )
    args = parser.parse_args()

    if _debug: _log.debug("initialization")
    if _debug: _log.debug("    - args: %r", args)

    # extract the server address and port
    host = args.host
    if host == "any":
        host = ''
    server_address = (host, args.port)
    if _debug: _log.debug("    - server_address: %r", server_address)

    # create a director listening to the address
    this_director = TCPServerDirector(server_address, idle_timeout=args.idle_timeout, actorClass=CustomActor)
    bind(CustomASE(), this_director)

    _log.debug("running")

    run()

    _log.debug("fini")


if __name__ == "__main__":
    main()
