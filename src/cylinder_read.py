#!/usr/bin/env python3
'''
Hotwater Cylinder - read temperature sensors and post Results to SQL database.

Sensor1 = Top of cylinder
Sensor2 =
Sensor3 =
Sensor4 =
Sensor5 = Bottom of cylinder

sql Table Column names
sensor_id: TEXT, sensor_name: TEXT, temperature: REAL, timestamp: INTEGER

SENSOR_LOOKUP = {sensor1:sensorID,
                sensor2:sensorID,
                sensor3:sensorID,
                sensor4,sensorID,
                sensor5,sensorID}

{sensorID:id, sensorName:name, temperature:temp, timeStamp:time}

Cron job will run script every Xmins
Read all sensors
Write values to rotating log file

'''

__author__ = "Keith Gough"
__version__ = "0.0.1"

import time
from textwrap import dedent
import getopt
import os
import sys
import logging.config

import sensor_DS18B20 as DS18B20
# import sqlite_kg_lib as sql

LOG_PATH = '/home/pi/repositories/telemetry/data_log.csv'
LOG_MAX_SIZE = 3000000

W1_DEVICES = '/sys/bus/w1/devices'
SENSOR_LOOKUP = {'28-0415a18d89ff': 'sensor1',
                 '28-0000076393f1': 'sensor2',
                 '28-0415a18c61ff': 'sensor3',
                 '28-0415a18b44ff': 'sensor4',
                 '28-0415a189ccff': 'sensor5'}

UWL_TARGET_TEMPERATURE = 40

DATABASE = '/home/pi/repositories/telemetry/sensordata.db'
TABLE = 'kg_water'
COLS = "(timestamp, sensor1, sensor2, sensor3, sensor4, sensor5)"


def get_args():
    """ Get command line arguments
    """
    args = {'save': False, }

    # Get command line options

    help_string = dedent("""
        USAGE: {} [-hs]

        -s        Save results to log file (default is no save).
        -h        Show this help

        """).format(os.path.basename(__file__))
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hs")
    except getopt.GetoptError as err:
        print(err.msg)
        sys.exit(2)
    for opt, _ in opts:
        if opt == '-s':
            args['save'] = True
        if opt == '-h':
            print(help_string)
            sys.exit()

    return args


def configure_logger(name, log_path=None, log_max_size=1024):
    """ Logger configuration function
        If logPath given then log to console and to the file
        else to console only.
    """
    version = 1
    disable_existing_loggers = False
    # formatters = {
    #     'default': {
    #         'format': '%(asctime)s,%(levelname)s,%(name)s,%(message)s',
    #         'datefmt': '%Y-%m-%d %H:%M:%S'
    #     }
    # }
    formatters = {'default': {'format': '%(message)s'}}

    console_handler = {'level': 'INFO',
                       'class': 'logging.StreamHandler',
                       'formatter': 'default',
                       'stream': 'ext://sys.stdout'}

    file_handler = {'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'default',
                    'filename': log_path,
                    'maxBytes': log_max_size,
                    'backupCount': 3}

    if log_path:
        logging.config.dictConfig({
            'version': version,
            'disable_existing_loggers': disable_existing_loggers,
            'formatters': formatters,
            'handlers': {'file': file_handler, 'console': console_handler},
            'loggers': {'': {'level': 'INFO', 'handlers': ['file']}}
        })
    else:
        logging.config.dictConfig({
            'version': version,
            'disable_existing_loggers': disable_existing_loggers,
            'formatters': formatters,
            'handlers': {'console': console_handler},
            'loggers': {'': {'level': 'INFO', 'handlers': ['console']}}
        })

    return logging.getLogger(name)


# def post_results_to_sqlite(results):
#     """ Insert the results into the mySQL DATABASE on the server
#
#     """
#     dbase = sql.Database(DATABASE)
#
#     vals = '("{}",{},{},{},{},{})'.format(results['timestamp'],
#                                           results['sensor1'],
#                                           results['sensor2'],
#                                           results['sensor3'],
#                                           results['sensor4'],
#                                           results['sensor5'],
#                                          )
#
#     dbase.insert_row(TABLE, COLS, vals)


def post_results_to_log_file(results):
    """ Write results to a rotating log file
    """
    logger = configure_logger(__name__, LOG_PATH, LOG_MAX_SIZE)
    data = (
        f"{results['timestamp']}," +
        f"{results['sensor1']}," +
        f"{results['sensor2']}," +
        f"{results['sensor3']}," +
        f"{results['sensor4']}," +
        f"{results['sensor5']}," +
        f"{results['uwl']}," +
        f"{results['timestamp']}"
    )
    logger.info(data)


def calc_uwl(s1_val, s3_val, target_val=UWL_TARGET_TEMPERATURE):
    """ We assume that usable hot water is any water >40'C

        Hot water is at the top of the tank

        S4 is on the same level as the top of the heating coils and over
        indicates when the hot water is on.

        S5 is on the inlet pipe.

        We note that the cyclinder Tstat is set at 55'C and that s3 indicates
        approx 40'C when the Tstat reaches the cutoff point, this is a 'full'
        tank.

        We want to know the 40'C point in the cylinder.  So we calculate the
        straight line between s1 and s3 and then use that to calculate the
        40'C position relative to S0.

        uwl is Usable Water Level (amount of 40'C in the tank)

        Calc uwl from y = mx + c

        y vals are temperatures
        x vals are sensor positions (we assume they are equally spaced)
        where x is UWL, c is s1 value, y = 40'C

        x = (y - c) / m

        uwl = (target_val - s1) / (s3 - s1)

        uwl = (40 - s1) / (s3 - s1)

        eg. for s1 = 50, s3=30 then uwl is halfway between the sensors

        uwl = (40-50)/(30-50) = 0.5

        e.g. s1=50, s3=40
        x = (40-50)/(40-50) = 1.0

        e.g. s1=50, s3=45
        uwl = (40-50)/(45-50) = 2.0 (i.e. uwl is below s3)
        In this case we should limit to 100%

        e.g. s1=38, s3=28
        uwl = (40 - 38) / (28 - 38) = 2/-10 = -0.2
        In this case we should limit to 0%

    """
    uwl = ((target_val - s1_val) / (s3_val - s1_val)) * 100

    uwl = max(uwl, 0)
    uwl = min(uwl, 100)

    return int(uwl)


def read_sensors(save_results=False):
    """ Read the sensors and return the results
    """
    # Confirm what devices are attached
    dev_ids = DS18B20.get_device_ids()

    time_stamp = int(time.time())
    results = {'timestamp': time_stamp}
    # time_stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for dev in dev_ids:

        # Lookup the sensor name using the id
        # If we don't find it then ignore it
        if dev not in SENSOR_LOOKUP:
            print('Sensor %s is not in the lookup TABLE', dev)
        else:
            temp, _ = DS18B20.get_temperature_reading(dev)
            sensor_name = SENSOR_LOOKUP[dev]
            results[sensor_name] = temp / 1000

    # Add UWL to the results
    results['uwl'] = calc_uwl(results['sensor1'], results['sensor3'])

    if save_results:
        post_results_to_log_file(results)
    else:
        # Print the results
        for i in range(1, 6):
            sensor = f"sensor{i}"
            print(f"{sensor} = {results[sensor]}")
        print(f"uwl = {results['uwl']}%")

    return results


if __name__ == "__main__":
    SAVE_RESULTS = get_args()
    read_sensors(SAVE_RESULTS['save'])
