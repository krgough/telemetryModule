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
import sys
import time

import api_methods as api
import config

import sensor_TSL2561 as TSL2561

NODE_NAME = 'Sitt Colour'

def main():
    """ Main Program """

    acct = api.SessionObject(config.USERNAME, config.PASSWORD, config.URL)

    start_percent = 1
    stop_percent = 100
    step_size = 1

    tsl = TSL2561.TSLl2561()
    auto_gain = False
    gain = '1x'
    int_time = '402ms'

    for level in range(start_percent, stop_percent + step_size, step_size):

        resp, success, payload = acct.set_brightness(NODE_NAME, level)
        if not success:
            print("API problem: {},{},{}".format(resp, success, payload))
            sys.exit(1)

        time.sleep(2)

        # Now read and print the levels for 1 min
        LUX, full_scaled, ir_scaled = tsl.get_lux(auto_gain, gain, int_time)
        print("{},{},{},{}".format(level, LUX, full_scaled, ir_scaled))

if __name__ == "__main__":
    main()
    print('All done.')
