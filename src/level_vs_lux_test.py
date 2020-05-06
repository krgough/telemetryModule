#!/usr/bin/env python3
'''
Created on 7 Mar 2016

@author: keith

Measure the LUX output for given illumination levels.

Loop for given number of steps:
    - Set the wanted level
    - Measure Lux for 1min
    - Results printed to console so redirect to file is advisable

'''
# pylint: disable=pointless-string-statement
import os
from getopt import getopt
import sys
import glob
from textwrap import dedent

import threaded_serial as AT
import read_light_levels as rll

""" Command line argument methods """
def get_args():
    """ Read command line parameters
        Use them if provided.
    """
    help_string = dedent("""
    
    USAGE: {} [-h] -n nodeId -e endpoint -p port -b baud
    Use these command line options to select the node, endpoint, uart port and baud
    
    -h             Print this help
    -n node        Node ID of target node
    -e endpoint    Endpoint of the target node
    -p port        /dev/portId
    -b baud        usually 115200""".format(os.path.basename(__file__)))

    node_id = None
    ep_id = None
    port = None
    baud = None

    opts = getopt(sys.argv[1:], "hn:e:p:b:")[0]

    for opt, arg in opts:
        #print(opt, arg)
        if opt == '-h':
            print(help_string)
            sys.exit()
        if opt == '-n':
            node_id = arg.upper()
        if opt == '-e':
            ep_id = arg
        if opt == '-p':
            port = arg
        if opt == '-b':
            baud = arg

    if not node_id:
        print("Node ID was not specified")
        print(help_string)
        sys.exit(1)

    if not ep_id:
        print("EP ID was not specified")
        print(help_string)
        sys.exit(1)

    if not port:
        print("UART port was not specified.  Try one of these...")
        print(glob.glob("/dev/tty.*"))
        print(help_string)
        sys.exit(1)

    if not baud:
        print("Baud rate not specified.  Typically we use 115200")
        print(help_string)
        sys.exit(1)

    return node_id, ep_id, port, baud

def set_level(node_id, ep_id, level):
    """ Set level
    """
    hex_level = "{:02x}".format(int(level / 100 * 254))
    resp_state, resp_code, resp_value = AT.move_to_level(node_id, ep_id, level=hex_level)
    if not resp_state:
        print("ERROR: move_to_level has failed. {}, {}".format(resp_code, resp_value))
        sys.exit(1)
def main():
    """ Main Program """
    node_id, ep_id, port, baud = get_args()

    AT.start_serial_threads(port,
                            baud,
                            print_status=False,
                            rx_q=True,
                            listener_q=False)

    start_percent = 10
    stop_percent = 100
    step_size = 10

    for level in range(start_percent, stop_percent + step_size, step_size):
        set_level(node_id, ep_id, level)

        # Now read and print the levels for 1 min
        rll.TAG = "{}%".format(level)
        rll.main(rll.params)

if __name__ == "__main__":
    main()
    print('All done.')
