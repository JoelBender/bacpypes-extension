# bacpypes-extension

Sample C modules for extending BACpypes

This repository contains sample Python extension modules written in C to be
used with BACpypes.

## udpserver

This sample module has a `Custom` class to be mixed in with a `Client` which
implements the `confirmation()` function for upstream packets from a
`UDPDirector` and provides a `request()` function to make it easier to
send packets.

## tcpserver

This sample module has a `Custom` class to be mixed in with a `TCPServerActor`
which implements the `response()` function for upstream packets from a
`TCPServer` and provides an `indication()` function to make it easier to
send packets.  The "flip" of the client/server pattern is because the default
behavour of an actor is to send upstream to a `TCPServerDirector`.

