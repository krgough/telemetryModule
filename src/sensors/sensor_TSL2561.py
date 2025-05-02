#!/usr/bin/env python3
# pylint: disable=invalid-name
'''
Created on 11 Jan 2016

@author: keith

TSL2561 Light Sensor - I2C LUX sensor

Default device address for adafruit board is 0x39
GND
3v
SDA
SCL

Requirements:

https://pypi.python.org/pypi/smbus2
sudo raspi-config << Use menus to enable I2C
pip install smbus2

i2cdetect -y 1 << Checks for devices attached to I2C-1

'''
# pylint: disable=pointless-string-statement

import time
import smbus2  # @UnresolvedImport

# PACKAGE_REG = 0x11 # Package register
# DEVICE_REG  = 0x12 # Device register
ADDRESS = 0x39     # I2C address
BUS_ADDRESS = 1    # Change to 0 for older RPi revision

# pylint: disable=bad-whitespace
# Register Addresses
TSL2561_REG_CONTROL          = 0x00
TSL2561_REG_TIMING           = 0x01
TSL2561_REG_THRESH_LOW_LOW   = 0x02
TSL2561_REG_THRESH_LOW_HIGH  = 0x03
TSL2561_REG_THRESH_HIGH_LOW  = 0x04
TSL2561_REG_THRESH_HIGH_HIGH = 0x05
TSL2561_REG_INTERRUPT        = 0x06
TSL2561_REG_ID               = 0x0A
TSL2561_REG_DATA0_LOW        = 0x0C
TSL2561_REG_DATA0_HIGH       = 0x0D
TSL2561_REG_DATA1_LOW        = 0x0E
TSL2561_REG_DATA1_HIGH       = 0x0F

# COMMAND Register Bits
TSL2561_CMD_BIT   = 0x80
TSL2561_CMD_CLEAR = 0x40
TSL2561_CMD_WORD  = 0x20
TSL2561_CMD_BLOCK = 0x10

# CONTROL Register Bits
TSL2561_CTRL_POWER_ON  = 0x03
TSL2561_CTRL_POWER_OFF = 0x00

# TIMING Regsister Bits
TSL2561_GAIN_VALS = {'1x':0x00,'16x':0x10}
#TSL2561_TIMING_GAIN_1X  = 0x00
#TSL2561_TIMING_GAIN_16X = 0x10

# Integration time values: 13ms,101ms,402ms
TSL2561_INT_VALS = {'13ms':0x00,'101ms':0x01,'402ms':0x02}
#TSL2561_TIMING_13MS  = 0x00  # 13.7ms
#TSL2561_TIMING_101MS = 0x01  # 101ms
#TSL2561_TIMING_402MS = 0x02  # 402ms

# Scaling parameter for integration time
TSL2561_13MS_SCALE = 322/11   # See device datasheet p.5
TSL2561_101MS_SCALE = 322/81  # See device datasheet p.5
TSL2561_402MS_SCALE = 322/322 # See device datasheet p.5

# Full scale values
TSL2561_13MS_FULL_SCALE  = 5047
TSL2561_101MS_FULL_SCALE = 37177
TSL2561_402MS_FULL_SCALE = 65535

# Lux Calculations coefficients
LUX_A1 = 0.0304
LUX_B1 = 0.062
LUX_A2 = 0.0224
LUX_B2 = 0.031
LUX_A3 = 0.0128
LUX_B3 = 0.0153
LUX_A4 = 0.00146
LUX_B4 = 0.00112

# pylint: enable=bad-whitespace

class TSL2561:
    # pylint: disable=too-many-instance-attributes
    """ Class to handle TSL2561 device """
    def __init__(self,
                 bus_address=BUS_ADDRESS,
                 sensor_address=ADDRESS,
                 integration='402ms',
                 gain='16x'):

        self.bus = smbus2.SMBus(bus_address)
        self.sensor_address = sensor_address
        self.sensor_error = None

        # Check device is present by reading the ID register
        self.dev_id = self.get_register(TSL2561_REG_ID)
        if not self.dev_id & 0x50:
            print("ERROR: Device ID should be 0x50.")
            return

        self.gain = gain
        self.integration_time = integration
        self.set_gain_and_integration()
        self.disable()

    @ property
    def gain(self):
        """ Return the gain setting """
        return self._gain
    @ property
    def integration_time(self):
        """ Return the integration time setting """
        return self._integration_time

    @ gain.setter
    def gain(self, gain_value):
        # Check we are trying to set a valid value
        if not gain_value in list(TSL2561_GAIN_VALS.keys()):
            print("ERROR: Invalid gain value.")
            print("{} is not in {}".format(gain_value, list(TSL2561_GAIN_VALS.keys())))
            return
        # If ok the set the value
        self._gain = gain_value
        self.set_gain_and_integration()
    @ integration_time.setter
    def integration_time(self, integration_time_value):
        # Check we are trying to set a valid value
        if not integration_time_value in list(TSL2561_INT_VALS.keys()):
            print("ERROR: Invalid integration time value.")
            print("{} is not in {}.".format(integration_time_value, list(TSL2561_INT_VALS.keys())))
        # If ok then set the value
        self._integration_time = integration_time_value
        self.set_gain_and_integration()

    def get_register(self, reg):
        """ Return the given register value
        """
        val = self.bus.read_byte_data(
            ADDRESS,
            TSL2561_CMD_BIT | reg)
        return val
    def enable(self):
        """ Enable the device
        """
        self.bus.write_byte_data(
            ADDRESS,
            TSL2561_CMD_BIT | TSL2561_REG_CONTROL,
            TSL2561_CTRL_POWER_ON)
    def disable(self):
        """ Disable the device
        """
        self.bus.write_byte_data(
            ADDRESS,
            TSL2561_CMD_BIT | TSL2561_REG_CONTROL,
            TSL2561_CTRL_POWER_OFF)
    def set_gain_and_integration(self):
        """ Sets the timing register to the gain and integration_time settings
        """
        gain_val = TSL2561_GAIN_VALS[self._gain]
        int_val = TSL2561_INT_VALS[self._integration_time]

        self.bus.write_byte_data(
            self.sensor_address,
            TSL2561_CMD_BIT | TSL2561_REG_TIMING,
            gain_val | int_val)
    def get_raw_luminosity(self):
        """ Get the luminosity value
        """
        #Turn on sensor
        self.enable()

        # Wait for integration to complete
        if self._integration_time == '13ms':
            time.sleep(0.020)
        elif self._integration_time == '101ms':
            time.sleep(0.150)
        elif self._integration_time == '402ms':
            time.sleep(0.450)

        full = self.bus.read_word_data(
            self.sensor_address,
            TSL2561_CMD_BIT | TSL2561_CMD_WORD | TSL2561_REG_DATA0_LOW)
        ir_lvl = self.bus.read_word_data(
            self.sensor_address,
            TSL2561_CMD_BIT | TSL2561_CMD_WORD | TSL2561_REG_DATA1_LOW)

        # Turn off sensor
        self.disable()
        return full, ir_lvl
    def get_raw_luminosity_auto_gain(self):
        """ Automatically adjusts gain to prevent saturation

            Start with full gain then select full gain if reading is over the threshold
            for the given integration_time

        """

        # Set max gain and get a reading
        self.gain = '16x'
        full, ir_lvl = self.get_raw_luminosity()

        if self._integration_time == '13ms':
            threshold = TSL2561_13MS_FULL_SCALE * 0.96
        elif self._integration_time == '101ms':
            threshold = TSL2561_101MS_FULL_SCALE * 0.96
        elif self._integration_time == '402ms':
            threshold = TSL2561_402MS_FULL_SCALE * 0.96

        # If reading greater than threshold then reduce gain
        if full > threshold:
            self.gain = '1x'
            full, ir_lvl = self.get_raw_luminosity()

        return full, ir_lvl
    def scale_raw_readings(self, full, ir_lvl, gain, integration_time):
        # pylint: disable=no-self-use
        """ Normalise the raw reading by scaling for gain and integration_time

        """
        if integration_time == '13ms':
            int_scale = TSL2561_13MS_SCALE
        if integration_time == '101ms':
            int_scale = TSL2561_101MS_SCALE
        if integration_time == '402ms':
            int_scale = TSL2561_402MS_SCALE

        if gain == '1x':
            gain_scale = 16
        if gain == '16x':
            gain_scale = 1

        full_scaled = round(full * int_scale * gain_scale)
        ir_scaled = round(ir_lvl * int_scale * gain_scale)

        return full_scaled, ir_scaled
    def lux_calculation(self, full, ir_lvl, gain, integration_time):
        """ Calculate LUX

            Scale for integration time and gain
            Calculate LUX

            use -1 as saturated value

        """
        # Scale the raw values
        full_scaled, ir_scaled = self.scale_raw_readings(full, ir_lvl, gain, integration_time)

        # Catch divide by zero
        if ir_lvl == 0:
            return 0, full_scaled, ir_scaled

        # Catch saturation
        if integration_time == '13ms' and full >= TSL2561_13MS_FULL_SCALE:
            return -1, full_scaled, ir_scaled
        if integration_time == '101ms' and full >= TSL2561_101MS_FULL_SCALE:
            return -1, full_scaled, ir_scaled
        if integration_time == '402ms' and full >= TSL2561_402MS_FULL_SCALE:
            return -1, full_scaled, ir_scaled

        # Calculate the LUX ratio
        ratio = ir_scaled / full_scaled
        #print(ratio)

        # Calculate LUX
        if ratio <= 0.5:
            lux = (LUX_A1 * full_scaled) - (LUX_B1 * full_scaled * (ratio ** 1.4))
        elif ratio <= 0.61:
            lux = (LUX_A2 * full_scaled) - (LUX_B2 * ir_scaled)
        elif ratio <= 0.8:
            lux = (LUX_A3 * full_scaled) - (LUX_B3 * ir_scaled)
        elif ratio <= 1.3:
            lux = (LUX_A4 * full_scaled) - (LUX_B4 * ir_scaled)
        elif ratio > 1.3:
            lux = 0

        lux = round(lux)
        return lux, full_scaled, ir_scaled

    ''' Use these methods to get the Luminosity readings and/or Lux value '''
    def get_scaled_luminosity(self, auto_gain=True):
        """ Get luminosity values scaled for gain and integration time.

        """
        if auto_gain:
            full, ir_lvl = self.get_raw_luminosity_auto_gain()
        else:
            full, ir_lvl = self.get_raw_luminosity()

        full_scaled, ir_scaled = self.scale_raw_readings(full,
                                                         ir_lvl,
                                                         self.gain,
                                                         self.integration_time)

        return full_scaled, ir_scaled
    def get_lux(self, auto_gain=True, gain='1x', int_time='402ms'):
        """ Get LUX value

        """
        if auto_gain:
            full, ir_lvl = self.get_raw_luminosity_auto_gain()
        else:
            self.gain = gain
            self.integration_time = int_time
            full, ir_lvl = self.get_raw_luminosity()

        lux, full_scaled, ir_scaled = self.lux_calculation(full,
                                                           ir_lvl,
                                                           self.gain,
                                                           self.integration_time)

        return lux, full_scaled, ir_scaled

def main():
    """ Main Program """
    tsl = TSL2561()
    print("DeviceID: {}".format(hex(tsl.dev_id)))

    full, ir_lvl = tsl.get_raw_luminosity()
    lux, full_scaled, ir_scaled = tsl.lux_calculation(full, ir_lvl, tsl.gain, tsl.integration_time)
    print("\nGain=16x. Full 402ms Integration time (max resolution)")
    print("RAW READINGS:    Full={:10}, ir_lvl={}".format(full, ir_lvl))
    print("SCALED READINGS: Full={:10}, ir_lvl={}".format(full_scaled, ir_scaled))
    print("LUX = {}".format(lux))

    tsl.gain = '1x'
    full, ir_lvl = tsl.get_raw_luminosity()
    lux, full_scaled, ir_scaled = tsl.lux_calculation(full, ir_lvl, tsl.gain, tsl.integration_time)
    print("\nGain=1x.  Full 402ms Integration Time (max resolution)")
    print("RAW READINGS:    Full={:10}, ir_lvl={}".format(full, ir_lvl))
    print("SCALED READINGS: Full={:10}, ir_lvl={}".format(full_scaled, ir_scaled))
    print("LUX = {}".format(lux))

    # Now use auto gain
    full, ir_lvl = tsl.get_raw_luminosity_auto_gain()
    lux, full_scaled, ir_scaled = tsl.lux_calculation(full, ir_lvl, tsl.gain, tsl.integration_time)
    print("\nAGC {} Gain selected.  402ms Integration Time (max resolution)".format(tsl.gain))
    print("RAW READINGS:    Full={:10}, ir_lvl={}".format(full, ir_lvl))
    print("SCALED READINGS: Full={:10}, ir_lvl={}".format(full_scaled, ir_scaled))
    print("LUX = {}".format(lux))

    # Use the recommended methods
    lux, full_scaled, ir_scaled = tsl.get_lux()
    print("\nSCALED READINGS: Full={:10}, ir_lvl={}".format(full_scaled, ir_scaled))
    print("LUX = {}".format(lux))

    print('\nAll Done')

if __name__ == "__main__":
    main()
