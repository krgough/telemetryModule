'''
Created on 2 Jan 2016

@author: keith
'''

import sys
import pylab as plt
import peewee_module as pw


NUMBER_OF_SENSORS = 5

SENSOR_CALIBRATION = {'sensor1':-172,
                      'sensor2':  61,
                      'sensor3': 248,
                      'sensor4': 266,
                      'sensor5':-403}

def get_data():
    """ Get the data
    """
    pw.sql_cred_id = 'kg_aws_keith'
    pw.database = 'hotwater'
    resp, err_status = pw.select_where(pw.db_Hotwater,
                                      pw.temperature,
                                      (pw.temperature.timestamp > "2016-01-16 00:00"))

    if err_status:
        print(err_status)
        sys.exit()

    # Build a dict of the form:
    #
    #    timestamp : {'sensor1':temperature1, 'sensor2':temperature2, ... ,'sensor5':temeprature5}
    #    timestamps will not be sorted so we build an index later.

    data = {}
    for reading in resp:
        if not reading.timestamp in data:
            data[reading.timestamp] = {}
        data[reading.timestamp][reading.sensorName] = reading.temperature

    # Now build an index.
    # Create a sorted list of timestamps.  Use this to index the data dict.

    sorted_timestamps = sorted(data)

    # Now we can print the data table
    # and create a dict of lists for the data

    sensor_data = {}
    for sensor in range(1, NUMBER_OF_SENSORS + 1):
        sensor_name = 'sensor{}'.format(sensor)
        sensor_data[sensor_name] = []

    print('Timestamp,sensor1,sensor2,sensor3,sensor4,sensor5')
    for timestamp in sorted_timestamps:
        print("{},{},{},{},{},{}".format(timestamp,
                                         data[timestamp]['sensor1'],
                                         data[timestamp]['sensor2'],
                                         data[timestamp]['sensor3'],
                                         data[timestamp]['sensor4'],
                                         data[timestamp]['sensor5']))

        for sensor in range(1, NUMBER_OF_SENSORS + 1):
            sensor_name = 'sensor{}'.format(sensor)
            sensor_data[sensor_name].append(data[timestamp][sensor_name])

    return sorted_timestamps, sensor_data
def plot_graph(x_range, y_range, number_of_lines):
    """ Plot a graph
    """
    for sensor in range(1, number_of_lines + 1):
        sensor_name = 'sensor{}'.format(sensor)
        plt.plot(x_range, y_range[sensor_name], label=sensor_name)

    # 111 = 1 row, 1 column, 1 plot
    axis = plt.subplot(111)
    # Shrink current axis by 20%
    box = axis.get_position()
    axis.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.grid()
    plt.show()

def main():
    """ Main Program """
    x_range, y_range = get_data()
    plot_graph(x_range, y_range, NUMBER_OF_SENSORS)

if __name__ == "__main__":
    main()
    print('All Done')
