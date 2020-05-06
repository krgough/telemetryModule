#!/usr/bin/env python3

""" UDP Server

Keith Gough, 01/05/2020

Waits for a Broadcast UDP message and sends a reply.

This one sends a message to the rpi on my local net asking for the hot water level
as measured from the sensors on the hot water cylinder.

Message:
uwl? = What is the usable water level

Expected Response:
uwl=xx.x%

Socket Notes:

Host id 'localhost' or '127.0.0.1' connects with other processes on the same computer
The computer can have more then one network card (NIC) and every NIC has own IP address.
Use a single IP to receive requests/connection from one NIC.
Use Empty string or '0.0.0.0' to  receive requests from all NICs.

"""

import socket
import logging

import cylinder_read as cyl

LOGGER = logging.getLogger(__name__)

# Create a UDP socket
# Setup to use the broadcast address
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

ADDRESS = ('', 10000)
UWL_MESSAGE = 'uwl?'
UWL_RESP = 'uwl='

# Bind the socket to the port
PORT = 10000
ADDR = ""
LOGGER.debug('Listening to all NICs on port %s', PORT)
SOCK.bind((ADDR, PORT))

def send_cmd(msg, expected_resp, addr):
    """ Send UDP message and wait for the expected response

    """
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

def listen_for_cmd():
    """ Listen for and reply to incomming commands
    """

    while True:
        LOGGER.debug('Waiting to receive message...')
        data, address = SOCK.recvfrom(4096)

        LOGGER.debug('Received %s bytes from %s, %s ', len(data), address, data)

        if data:
            message = "uwl={}%".format(cyl.read_sensors()['uwl'])
            SOCK.sendto(message.encode(), address)
            #print('sent %s bytes back to %s' % (sent, address))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    listen_for_cmd()
