'''
Created on 1 Jul 2016

@author: keith

Measure the LUX output for a given illumination levels.
Soak for some extended period
Results printed to console so redirect to file is advisable

'''

from os import path
from getopt import getopt
import sys
import glob

import threaded_serial as AT
import sensors.read_light_levels as rll


def get_args():
    """ Read command line parameters
        Use them if provided.
    """
    help_string = f"\nUSAGE: {path.basename(sys.argv[0])} [-h] -n nodeId -e endpoint -p port -b baud\n\n" +\
                 "Use these command line options to select the node, endpoint, uart port and baud\n\n" +\
                 "-h             Print this help\n" +\
                 "-n node        Node ID of target node\n" +\
                 "-e endpoint    Endpoint of the target node\n" +\
                 "-p port        /dev/portId\n" +\
                 "-b baud        usually 115200\n"

    node_id = None
    ep = None
    port = None
    baud = None

    opts = getopt(sys.argv[1:], "hn:e:p:b:")[0]

    for opt, arg in opts:
        # print(opt, arg)
        if opt == '-h':
            print(help_string)
            exit()
        if opt == '-n':
            node_id = arg.upper()
        if opt == '-e':
            ep = arg
        if opt == '-p':
            port = arg
        if opt == '-b':
            baud = arg

    if not node_id:
        print("Node ID was not specified")
        print(help_string)
        sys.exit()

    if not ep:
        print("EP ID was not specified")
        print(help_string)
        sys.exit()

    if not port:
        print("UART port was not specified.  Try one of these...")
        print(glob.glob("/dev/tty.*"))
        print(help_string)
        sys.exit()

    if not baud:
        print("Baud rate not specified.  Typically we use 115200")
        print(help_string)
        sys.exit()

    return node_id, ep, port, baud


def set_level(node_id, ep_id, level):
    """ set the level of the light """
    level = f"{int(level/100*254):02x}"

    resp_state, resp_code, resp_value = AT.move_to_level(node_id, ep_id, level=level)
    if not resp_state:
        print(f"ERROR: move_to_level has failed. {resp_code} {resp_value}")
        sys.exit()


def main():
    """ Entry point """
    node_id, ep, port, baud = get_args()
    AT.start_serial_threads(port, baud, print_status=False, rx_q=True, listener_q=False)

    level = 70  # Light level as percentage
    set_level(node_id, ep, level)

    # Now read and print the levels for 1 min
    rll.TAG = f"{level}%"
    rll.params['duration'] = 60*60*2  # 2 hours
    rll.params['period'] = 1          # 1 second
    rll.main(rll.params)


if __name__ == "__main__":
    main()
    print('All done.')
