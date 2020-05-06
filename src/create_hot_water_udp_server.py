#!/usr/bin/env python3

""" Start the hot water UDP Server or skip if already running

Server will reply to 'uwl?' UDP message with a message containing the estimated
hot water level in the hot water cylinder.  This script check the server is
running and if not then it starts it.

"""
__author__ = "Keith Gough"
__version__ = "0.0.1"

import logging
import subprocess
import psutil

LOGGER = logging.getLogger(__name__)
PROC_CMD_LINE = "/hot_water_udp_server.py"

def check_process(proc_name):
    """ Check if process is running
    """

    ps = subprocess.Popen(('ps', '-ef'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('grep', '/hot_water_udp_server.py'), stdin=ps.stdout)

    print(output.decode())

def check_process2(proc_name):
    """
    """
    procs = psutil.process_iter()

    for proc in procs:
        try:
            cmd = " ".join(proc.cmdline())
            if cmd.find(proc_name) > 0:
                print(cmd)
        except psutil.AccessDenied:
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    check_process2(PROC_CMD_LINE)
