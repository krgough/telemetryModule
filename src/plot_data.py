#!/usr/bin/env python3
'''
Created on 22 Apr 2020

@author: Keith.Gough
'''
from datetime import datetime
import matplotlib.pyplot as plt


FILENAME = 'data_log.csv'
NUMBER_OF_SENSORS = 5

def convert_timestamps(timestamp_list):
    """ Convert the timestamp data to a list of datetime types
    """
    return [datetime.fromtimestamp(int(ts)) for ts in timestamp_list]
def load_data_from_file(filename):
    """ Load data from csv file to a list of lists
        First row of list has headers
    """
    with open(filename, mode='r') as file:
        data = file.readlines()
        data = [line.strip().split(',') for line in data]

    # Unpack the list of lists
    data = list(zip(*data))

    # Change types
    data[0] = [int(val) for val in data[0]]

    for i, _ in enumerate(data[1:]):
        data[i + 1] = [float(val) for val in data[i + 1]]

    x_vals = data[0]
    y_vals = data[1:]

    x_vals = [datetime.fromtimestamp(val) for val in x_vals]

    return x_vals, y_vals

def calc_uwl(s0_val, s2_val, target_val=40):
    """ We assume that usable hot water is any water >40'C

        Hot water is at the top of the tank, S0,S1,S2

        S3 is on the same level as the top of the heating coils and over indicates
        when the hot water is on.

        S4 is on the inlet pipe.

        We note that the cyclinder Tstat is set at 55'C and that s2 indicates approx
        40'C when the Tstat reaches the cutoff point, this is a 'full' tank.

        We want to know the 40'C point in the cylinder.  So we calculate the straight
        line between s0 and s2 and then use that to calculate the 40'C position
        relative to S0.

        uwl is Usable Water Level (amount of 40'C in the tank)

        Calc uwl from y = mx + c

        y vals are temperatures
        x vals are sensor positions (we assume they are equally spaced)
        where x is UWL, c is s0 value, y = 40'C

        x = (y - c) / m

        uwl = (target_val - s0) / (s2 - s0)

        uwl = (40 - s0) / (s2 - s0)

        eg. for s0 = 50, s2=30 then uwl is halfway between the sensors

        uwl = (40-50)/(30-50) = 0.5

        e.g. s0=50, s2=40
        x = (40-50)/(40-50) = 1.0

        e.g. s0=50, s2=45
        uwl = (40-50)/(45-50) = 2.0 (i.e. uwl is below s2)
        In this case we should limit to 100%

        e.g. s0=38, s2=28
        uwl = (40 - 38) / (28 - 38) = 2/-10 = -0.2
        In this case we should limit to 0%

    """
    uwl = (target_val - s0_val) / (s2_val - s0_val)

    if uwl < 0:
        uwl = 0
    if uwl > 1:
        uwl = 1

    return uwl * 100

def create_uwl_data(data):
    """
    """
    s0_data = data[0]
    s2_data = data[2]

    uwl_data = []
    for i, s0_val in enumerate(s0_data):
        s2_val = s2_data[i]
        uwl_val = calc_uwl(s0_val, s2_val, target_val=40)
        uwl_data.append(uwl_val)

    return uwl_data

def main():
    """ Main Program """

    x_vals, data = load_data_from_file(FILENAME)

    # Add uwl to the data
    data.append(create_uwl_data(data))

    plt.rcParams["date.autoformatter.minute"] = "%Y-%m-%d %H:%M:%S"
    fig, sub_plots = plt.subplots()
    sub_plots.grid()

    for i, y_vals in enumerate(data):
        #sub_plots.plot(x_vals, y_vals, label='Sxx', linestyle='--', marker='o')
        sub_plots.plot(x_vals, y_vals, label='S_{}'.format(i), marker='o')

    # Shrink current axis by 20%
    box = sub_plots.get_position()
    sub_plots.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    sub_plots.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    sub_plots.set_title("KG Water Temperatures")
    plt.show()


if __name__ == '__main__':
    main()
