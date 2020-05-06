#!/usr/bin/env python3
'''
Created on 18 Jan 2016

@author: keith

Light Levels - Read light level sensor.

-i integration_time. 13ms, 101ms or 402ms. Usage example, -i 13
-g integrationGain. 1x or 16x. Usage example, -g 16
-d duration. How long to run this script for in seconds.
-p period. How often to take a reading in seconds.
           Default (if not specified) is to read as fast as possible.
           Rate is limited by how fast we can read the I2C bus and the integration time.

'''
import time
import getopt
import sys
import os
from textwrap import dedent

import sensor_TSL2561 as TSL5661

# Free text field for labelling measurements e.g. location of measuremnt or bulb level
TAG = 'myMeasurement'

DEFAULT_PARAMS = {'integration_time':'402ms',
                  'integrationGain':'16x',
                  'duration':60,     # Duration to run the script for in seconds.
                                     # Default=0 i.e. one run only.
                  'period':0}        # Frequency of readings in seconds

TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

def get_args(params):
    """ Get CLI arguments
    """
    help_string = dedent("""
    
    Usage: {} [-h]
    -h show help
    -i integration_time. 13ms,101ms or 402ms. Usage: -i 13
    -g integrationGain. 1x or 16x. Usage: -g 16
    -d duration. How long to run this script for in seconds
    -p period. How often to take a reading in seconds.
               Default (if not specified) is to read as fast as possible.
               Rate is limited by how fast we can read the I2C bus and the integration time.
    """.format(os.path.basename(__file__)))

    # First arg is the pathname for the current file
    # Remaining args are those provided on the command line
    try:
        options, _ = getopt.getopt(sys.argv[1:], "hi:g:d:p:")

    except getopt.GetoptError as err:
        print(err)
        print('\n*** INVALID OPTIONS')
        print(help_string)
        sys.exit()

    for opt, arg in options:
        if opt == '-h':
            print(help_string)
            sys.exit(1)
        elif opt == '-i':
            if arg in ('13', '101', '402'):
                params['integration_time'] = arg + 'ms'
            else:
                print(help_string)
                sys.exit(1)
        elif opt == '-g':
            if arg in ('1', '16'):
                params['integrationGain'] = arg + 'x'
            else:
                print(help_string)
                sys.exit(1)
        elif opt == '-d':
            params['duration'] = int(arg)
        elif opt == '-p':
            params['period'] = float(arg)

    return params
def read_sensor(sensor):
    """ Read the sensor and return the measured values

    """
    # Get the readings
    LUX, full_scaled, ir_scaled = sensor.get_lux()
    timestamp = time.time()
    results = ({'tag':TAG,
                'full':full_scaled,
                'ir':ir_scaled,
                'LUX':LUX,
                'gain':sensor.gain,
                'integration_time':sensor.integration_time,
                'timestamp':timestamp})

    return results

def main():
    """ Main Program """

    params = get_args(DEFAULT_PARAMS)
    print("INTEGRATION TIME: {}".format(params['integration_time']))
    print("INTEGRATION GAIN: {}".format(params['integrationGain']))
    print("DURATION        : {}".format(params['duration']))
    print("PERIOD          : {}".format(params['period']))

    sensor = TSL5661.TSLl2561(gain=params['integrationGain'],
                             integration=params['interationTime'])

    start_time = time.time()

    while True:
        results = read_sensor(sensor)
        print("{},{},{},{},{},{},{}".format(results['timestamp'],
                                            results['tag'],
                                            results['LUX'],
                                            results['gain'],
                                            results['integration_time'],
                                            results['full'],
                                            results['ir']))
        #print(results)
        time.sleep(params['period'])
        if time.time() > start_time + params['duration']:
            break

if __name__ == "__main__":
    main()
