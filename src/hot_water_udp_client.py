#!/usr/bin/env python3

""" UDP Client

Keith Gough, 01/05/2020

Send a Broadcast UDP message and wait for a reply.
This one sends a message to the rpi on my local net asking for the hot water level
as measured from the sensors on the hot water cylinder.

Message:
uwl? = What is the usable water level

Expected Response:
uwl=xx.x%

"""

import socket
import logging

LOGGER = logging.getLogger(__name__)

# Create a UDP socket
# Setup to use the broadcast address
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

SOCK.settimeout(10)

ADDRESS = ('255.255.255.255', 10000)
UWL_MESSAGE = 'uwl?'
UWL_RESP = 'uwl='

def send_cmd(msg, expected_resp, addr):
    """ Send UDP message and wait for the expected response

    """
    LOGGER.debug("socket using address: %s", ADDRESS)
    LOGGER.debug("socket timeout is: %ss", SOCK.gettimeout())

    # Send data
    LOGGER.debug('sending %s', msg)
    SOCK.sendto(msg.encode(), addr)

    # Receive response
    LOGGER.debug('waiting to receive')

    try:
        data, server = SOCK.recvfrom(4096)
        LOGGER.debug('received "%s", from %s', data.decode(), server)
        if data.decode().startswith(expected_resp):
            data = data.decode()[len(expected_resp):]
    except socket.timeout:
        data = None

    LOGGER.debug('closing socket')
    SOCK.close()
    return data

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print(send_cmd(UWL_MESSAGE, UWL_RESP, ADDRESS))
