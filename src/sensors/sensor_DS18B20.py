#!/usr/bin/env python3
# pylint: disable=invalid-name
'''
Created on 16 Jan 2016

@author: keith

DS18B20 Temperature Sensor Library

One wire data bus sensor.  Multiple sensors on one GPIO.
Sensor has 3 connections, 3v3, GND and Signal.  Signal should be pulled to 3v3 via
external 4k7.

Enable w1 using....

sudo dtoverlay w1-gpio gpiopin=4 pullup=0
  or
raspi-config

'''
# pylint: disable = pointless-string-statement

import os
import sys
import time

#import mySqlLibrary as sql

# Enable the w1 system bus
#os.system('sudo dtoverlay w1-gpio gpiopin=4 pullup=0')

NULL_TEMPERATURE = 999
W1_DEVICES = '/sys/bus/w1/devices'
DEBUG = False


class W1_Sensor:
    """ Class for DS18B20 one wire sensors """
    def __init__(self, dev_id):
        self.id = dev_id
        self.temperature = None
        self.timestamp = None
        self.reading = None

    def read_sensor(self):
        """ Read temperature value for this sensor """

        #self.timestamp = time.strftime("%Y-%m-%dev %H:%M:%S")
        self.timestamp = time.time()

        try:
            with open("{}/{}/w1_slave".format(W1_DEVICES, self.id)) as file:
                self.reading = file.read()

            """
            Reading has the form..
            
            3c 01 4b 46 7f ff 0c 10 36 : crc=36 YES
            3c 01 4b 46 7f ff 0c 10 36 t=19750
            
            check for a 'YES"
            """
            read_ok = bool(self.reading.find('YES') > 0)

            if read_ok:
                self.temperature = int(self.reading.split("\n")[1].split("=")[1])/1000
            else:
                self.temperature = None

        except FileExistsError:
            err = sys.exc_info()[0]
            self.reading = err
            self.temperature = None

    def __repr__(self):
        """ Returns the object representation
        """
        return str(self.temperature)

def get_device_ids():
    """ Get the device IDs
    """

    ids = [dev for dev in os.listdir(W1_DEVICES) if dev.startswith("28-")]

    #my_names = os.listdir(W1_DEVICES)
    #ids = []
    #for dev in my_names:
    #    if dev.startswith("28-"):
    #        ids.append(dev)

    return ids
def get_temperature_reading(dev_id):
    """ Get the temperature
    """
    try:
        with open("{}/{}/w1_slave".format(W1_DEVICES, dev_id)) as file:
            my_text = file.read()

        """
        Reading has the form..
        
        3c 01 4b 46 7f ff 0c 10 36 : crc=36 YES
        3c 01 4b 46 7f ff 0c 10 36 t=19750
        
        check for a 'YES"
        """
        read_ok = bool(my_text.find('YES') > 0)

        if read_ok:
            temperature = int(my_text.split("\n")[1].split("=")[1])
            status_code = 'ReadingOK'
        else:
            temperature = NULL_TEMPERATURE
            status_code = my_text

    except FileExistsError:
        err = sys.exc_info()[0]
        status_code = err
        temperature = 999

    return temperature, status_code

def main():
    """ Main Program """

    dev_ids = get_device_ids()
    if DEBUG:
        print(dev_ids)

    # Create a list of sensor objects.
    sensors = []
    for dev_id in get_device_ids():
        sensors.append(W1_Sensor(dev_id))

    # Read each sensor
    for sensor in sensors:
        sensor.read_sensor()

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(timestamp, end=': ')
    print(', '.join([str(sensor.temperature) for sensor in sensors]))

    print("All Done.")

if __name__ == "__main__":
    main()
