#!/usr/bin/env python3

# pylint: disable=line-too-long
'''
Hotwater Cylinder - read temperature sensors

Sensor1 = Top of cylinder
Sensor2 =
Sensor3 =
Sensor4 =
Sensor5 = Bottom of cylinder

# Rotating log file storage
Data is written to a rotating log file with the name `data_log.csv`
The file is rotated every 60days

# Database storage
- create an sqlite3 database `sqlite3 database.db`
- create table water_data(timestamp TEXT, sensor1 INTEGER, sensor2 INTEGER, sensor3 INTEGER, sensor4 INTEGER, sensor5 INTEGER);

- To drop the table `drop table kg_water;`
- To insert data into the table
`insert into kg_water(timestamp, sensor1, sensor2, sensor3, sensor4, sensor5) values(?, ?, ?, ?, ?, ?);`

'''
# pylint: enable=line-too-long

from argparse import ArgumentParser
import time
import logging.config

import src.sensors.sensor_DS18B20 as DS18B20


LOG_PATH = '/home/pi/repositories/telemetryModule/data_log.csv'
LOG_MAX_SIZE = 3000000

W1_DEVICES = '/sys/bus/w1/devices'
SENSOR_LOOKUP = {
    '28-0415a18d89ff': 'sensor1',
    '28-0000076393f1': 'sensor2',
    '28-0415a18c61ff': 'sensor3',
    '28-0415a18b44ff': 'sensor4',
    '28-0415a189ccff': 'sensor5'
}

UWL_TARGET_TEMPERATURE = 40

DATABASE = '/home/pi/repositories/telemetryModule/sensordata.db'
TABLE = 'kg_water'
COLS = "(timestamp, sensor1, sensor2, sensor3, sensor4, sensor5)"


def get_args():
    """ Get command line arguments """
    parser = ArgumentParser(
        description="Read the temperature sensors and optionally save result to a file or database",
        epilog="Example: python3 cylinder_read.py -s data_log.csv",
    )

    subparsers = parser.add_subparsers(
        title="Save options",
        description="Choose to save results to a file or database",
        help="Save results to a file or database",
        dest="command"
    )

    file_parser = subparsers.add_parser(
        "file",
        help="Save results to the given csv log file"
    )
    database_parser = subparsers.add_parser(
        "database",
        help="Save results to the given database"
    )

    file_parser.add_argument(
        "--file",
        metavar="log_file.csv",
        type=str,
        help="Path to the log file",
        default=LOG_PATH
    )

    database_parser.add_argument(
        "--database",
        metavar="database.db",
        type=str,
        help="SQLite Database file"
    )
    database_parser.add_argument(
        "-t",
        metavar="table_name",
        type=str,
        help="Table name in the database"
    )

    return parser.parse_args()


def configure_logger(log_path=None, log_max_size=1024):
    """ Logger configuration function
    If logPath given then log to console and to the file else to console only.
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
            'loggers': {'': {'level': 'INFO', 'handlers': ['file', 'console']}}
        })
    else:
        logging.config.dictConfig({
            'version': version,
            'disable_existing_loggers': disable_existing_loggers,
            'formatters': formatters,
            'handlers': {'console': console_handler},
            'loggers': {'': {'level': 'INFO', 'handlers': ['console']}}
        })

    return logging.getLogger(__name__)


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


def calc_uwl(s1_val, s3_val, target_val=UWL_TARGET_TEMPERATURE):
    """ We assume that usable hot water is any water >40'C

        Hot water is at the top of the tank

        S4 is on the same level as the top of the heating coils and over
        indicates when the hot water is on.

        S5 is on the inlet pipe.

        We note that the cyclinder Tstat is set at 55'C and that S3 indicates
        approx 40'C when the Tstat reaches the cutoff point, this is a 'full'
        tank.

        We want to know the 40'C point in the cylinder.  So we calculate the
        straight line between S1 and S3 and then use that to calculate the
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

    # If the top of the tank is colder than the target then the
    # cyclinder is completely empty
    if s1_val < target_val:
        uwl = 0

    # If the bottom of the tank is hotter than the target then
    # the cylinder is completely full
    elif s3_val >= target_val:
        uwl = 100

    # Find the 40'C point in the tank as a percentage
    else:
        m = s3_val - s1_val
        c = s1_val
        uwl = round(((target_val - c) / m) * 100)

    return uwl


def read_sensors():
    """ Read the sensors and return the results """
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

    # Print the results
    for i in range(1, 6):
        sensor = f"sensor{i}"
        print(f"{sensor} = {results[sensor]}")
    print(f"uwl = {results['uwl']}%")

    return results


def test_uwl_calc():
    """ Test the UWL calculation
    """
    test_cases = [
        (60, 30, 40, 67),
        (60, 39, 40, 95),
        (41, 20, 40, 5),
        (50, 30, 40, 50),
        (50, 40, 40, 100),
        (50, 45, 40, 100),
        (38, 28, 40, 0),
        (50, 50, 40, 100),
        (30, 30, 40, 0),
        (40, 40, 40, 100)
    ]

    for s1_val, s3_val, _, expected in test_cases:
        result = calc_uwl(s1_val, s3_val)
        assert result == expected, f"Expected {expected}, got {result}"


def main(args):
    """ Entry point """

    test_uwl_calc()

    data = read_sensors()
    LOGGER.info(data)

    if args.command == "database":
        # Save results to a database
        LOGGER.info("Saving results to %s", args.database)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    ARGS = get_args()
    if ARGS.command == "file":
        LOGGER = configure_logger(log_path=ARGS.file, log_max_size=LOG_MAX_SIZE)
    else:
        LOGGER = configure_logger()
    main(args=ARGS)
