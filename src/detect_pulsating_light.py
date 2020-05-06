#!/usr/bin/env python3
'''
Created on 19 Jul 2016

@author: keith

Test to try and recreate pulsating LED bulb

Soak at 70% for 30mins and then switch to off or 100% for some time.
Repeat while measuring max min levels

'''

import time
import datetime
from textwrap import dedent
import random
import os
from getopt import getopt
import sys
import glob


import threaded_serial as AT
import sensor_TSL2561 as TSL5661

TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

""" Command line argument methods """
def get_args():
    """ Read command line parameters
        Use them if provided.
    """
    help_string = dedent("""

    USAGE: {} [-h] -n nodeId -e endpoint -p port -b baud\n\n".format(path.basename(sys.argv[0])) +\
    Use these command line options to select the node, endpoint, uart port and baud\n\n" +\
    -h             Print this help\n" +\
    -n node        Node ID of target node\n" +\
    -e endpoint    Endpoint of the target node\n" +\
    -p port        /dev/portId\n" +\
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
            sys.exit(1)
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
    """ Set the level
    """
    level = "{:02x}".format(int(level / 100 * 254))

    resp_state, resp_code, resp_value = AT.move_to_level(node_id, ep_id, level=level)
    if not resp_state:
        print("ERROR: move_to_level has failed. {}, {}".format(resp_code, resp_value))
        sys.exit(1)

def soak_test(node_id, ep_id, level, soak_time):
    """ Sets the bulb to a given level for a given time and returns the max,min LUX levels
        measured during that period.

        level is 0-100%
        soak_time is in seconds

    """
    # Light level as percentage
    set_level(node_id, ep_id, level)
    time.sleep(5)

    # Setup the sensor
    sensor = TSL5661.TSLl2561()
    LUX, _, _ = sensor.get_lux()
    min_lux = LUX
    max_lux = min_lux

    timeout = time.time() + soak_time
    while time.time() < timeout:
        LUX, _, _ = sensor.get_lux()
        if LUX < min_lux:
            min_lux = LUX
        if LUX > max_lux:
            max_lux = LUX

    return min_lux, max_lux
def main():
    """ Main Program """
    print("*** Pulsating lamp checkGainAndAgc")
    print("Soaking at 70% for 30mins then at a random level for 5mins")
    print("Measure max,mix LUX during 30min soak")
    print("Assumption is that we get a larger slow variation but this will not detect the problem")
    print("if the bulb varies normally by the same amount but too quickly to see.")

    # Create a results file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    result_file = '/home/pi/pulsatingBulbResult_{}'.format(timestamp)

    # Setup the bulb
    node_id, ep_id, port, baud = get_args()
    AT.start_serial_threads(port, baud, print_status=False, rx_q=True, listener_q=False)

    print("\nSetting bulb to 100% initially...")
    level = 100 # Light level as percentage
    set_level(node_id, ep_id, level)
    time.sleep(5)
    print("\nStarting iterations...")

    for i in range(1, 100):
        # Soak at 70% for 30mins
        min_lux, max_lux = soak_test(node_id, ep_id, 70, 30 * 60)
        timestamp = datetime.datetime.now().strftime(TIME_FORMAT)
        my_string = "Interation={},{},{},{},{}".format(i,
                                                       timestamp,
                                                       min_lux,
                                                       max_lux,
                                                       max_lux - min_lux)

        print(my_string)
        with open(result_file, 'a') as file:
            print(my_string, file=file)

        # Set level to random value for 5mins
        level = random.randint(0, 100)
        set_level(node_id, ep_id, level)
        time.sleep(5 * 50)

if __name__ == "__main__":
    main()
    print('All done.')
