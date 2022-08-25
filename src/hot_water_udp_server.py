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
import sys
import os
import time
import threading

import cylinder_read as cyl

# Using the configure_logger procedure to setup the logging to a file
# LOGGER = logging.getLogger(__name__)

# Create a UDP socket
# Setup to use the broadcast address
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
SOCK.settimeout(120)

# Bind the socket to the port
PORT = 10000
ADDR = ""
SOCK.bind((ADDR, PORT))

UWL_MESSAGE = 'uwl?'
UWL_RESP = 'uwl='

LOGFILE = "/tmp/hot_water_swerver.log"

def configure_logger(logger_name, log_path=None):
    """ Logger configuration function
        If log_path given then log to console and to the file
        else to console only.
    """
    version = 1
    disable_existing_loggers = False
    formatters = {'default': {'format': '%(asctime)s,%(levelname)s,%(name)s,%(message)s',
                              'datefmt': '%Y-%m-%d %H:%M:%S'}
                 }

    console_handler = {'level': 'DEBUG',
                       'class': 'logging.StreamHandler',
                       'formatter': 'default',
                       'stream': 'ext://sys.stdout'}

    file_handler = {'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'default',
                    'filename': log_path,
                    'maxBytes': 100000,
                    'backupCount': 3}

    if log_path:
        logging.config.dictConfig({
            'version': version,
            'disable_existing_loggers': disable_existing_loggers,
            'formatters': formatters,
            'handlers': {'file': file_handler},
            'loggers': {'':{'level': 'DEBUG', 'handlers': ['file']}}
        })
    else:
        logging.config.dictConfig({
            'version': version,
            'disable_existing_loggers': disable_existing_loggers,
            'formatters': formatters,
            'handlers': {'console': console_handler},
            'loggers': {'':{'level': 'DEBUG', 'handlers': ['console']}}
        })

    logging.getLogger('requests').setLevel(logging.WARNING)

    return logging.getLogger(logger_name)

def send_cmd(msg, expected_resp, addr):
    """ Send UDP message and wait for the expected response

    """
    # Send data
    LOGGER.debug('sending %s', msg)
    SOCK.sendto(msg.encode(), addr)

    # Receive response
    LOGGER.debug('waiting to receive')

    try:
        data, server = SOCK.recvfrom(1024)
        LOGGER.debug('received "%s", from %s', data.decode(), server)
        if data.decode().startswith(expected_resp):
            data = data.decode()[len(expected_resp):]
    except socket.timeout:
        data = None

    LOGGER.debug('closing socket')
    SOCK.close()
    return data

def uwl_worker(uwl):
    """ This thread worker runs every 2 mins and updates the
        uwl value so we always have the latest value to serve
        out to clients.

        We use a list for this as that is in shared memory
        between threads
    """
    while True:
        uwl[0] = cyl.read_sensors()['uwl']
        LOGGER.debug('uwl=%s', uwl[0])
        time.sleep(120)

def listen_for_cmd():
    """ Listen for and reply to incomming commands
    """
    # Setup and start the thread that gets uwl regularly
    uwl = [None]
    uwl_thread = threading.Thread(target=uwl_worker, args=(uwl,))
    uwl_thread.daemon = True
    uwl_thread.start()

    while True:
        #LOGGER.debug('calculating uwl...')
        #uwl = cyl.read_sensors()['uwl']
        #LOGGER.debug('uwl=%s', uwl)

        LOGGER.debug('Waiting to receive message...')
        try:
            data, address = SOCK.recvfrom(1024)
        except socket.timeout:
            data = None

        if data:
            LOGGER.debug('Received %s bytes from %s, %s ', len(data), address, data)
            if data.decode().startswith(UWL_MESSAGE):
                message = "{}{}%".format(UWL_RESP, uwl[0])
                SOCK.sendto(message.encode(), address)

        # Check the uwl thread is alive and restart if not
        if not uwl_thread.is_alive():
            LOGGER.debug("uwl thread is not alive.  Exiting for a clean re-start...")
            sys.exit()

if __name__ == "__main__":
    LOGGER = configure_logger(os.path.basename(__file__), LOGFILE)
    LOGGER.debug("Hot Water UDP server starting...")
    LOGGER.debug('Listening to all NICs on port %s', PORT)

    listen_for_cmd()
