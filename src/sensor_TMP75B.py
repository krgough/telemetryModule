#!/usr/bin/env python3
# pylint: disable=invalid-name
'''
Created on 13 Mar 2018

@author: Keith.Gough

TMP75B I2C Temperature Sensor

'''
import sys
import time
import smbus2  # @UnresolvedImport

# pylint: disable=bad-whitespace

# Address values
BUS_ADDRESS = 0x01   # I2C 1 on rPi
DEV_ADDRESS = 0x48   # Address for the TMP75B IC

# Register Addresses
TMP75B_REG_TEMP   = 0x00
TMP75B_REG_CONF   = 0x01
TMP75B_REG_T_LOW  = 0x02
TMP75B_REG_T_HIGH = 0x03

# Config Register Mask Bits
TMP75B_CFG_OS  = 0x8000  # One shot mode - write 1 to start a conversion, (if SD=1)
TMP75B_CFG_CR  = 0x6000  # Conversion rate control
TMP75B_CFG_FQ  = 0x1800  # Fault Q to trigger the alert pin
TMP75B_CFG_POL = 0x0400  # Alert polarity control         0=Alert active low, 1=Alert active hight
TMP75B_CFG_TM  = 0x0200  # Alert thermostat mode control. 0=comparator mode, 1=Interrupt mode
TMP75B_CFG_SD  = 0x0100  # Shutdown control bit.          0=continuous, 1=shutdown

# Config Register Settings Bits
TMP75B_CFG_CR_37 = 0x0000
TMP75B_CFG_CR_18 = 0x2000
TMP75B_CFG_CR_09 = 0x4000
TMP75B_CFG_CR_04 = 0x6000

TMP75B_CFG_FQ_01 = 0x0000
TMP75B_CFG_FQ_02 = 0x0800
TMP75B_CFG_FQ_04 = 0x1000
TMP75B_CFG_FQ_06 = 0x1800

TMP75B_RESET_CONFIG = 0x00FF

# pylint: enable=bad-whitespace

DEBUG = False

class TMP75B:
    """ Class for handling TMP75B device """
    def __init__(self, bus_address=BUS_ADDRESS, device_address=DEV_ADDRESS):
        self.bus_address = bus_address
        self.device_address = device_address

        self.bus = smbus2.SMBus(self.bus_address)

        # Check if device is present by reading the config reg
        val = self.read_word(TMP75B_REG_CONF)
        if (val & 0x00FF) != 0x00FF:
            print("ERROR: Device not found at adddress {}".format(self.device_address))
            print("{:04x}".format(val))
            sys.exit(1)

        # Do a reset
        self.reset_config()

    def byte_swap(self, val):
        # pylint: disable=no-self-use
        """ Swap bytes in val """
        low_b = (0xff00 & val) >> 8
        hi_b = (0x00ff & val) << 8
        return low_b | hi_b
    def read_byte(self, reg):
        """ Read a byte from the bus """
        return self.bus.read_byte_data(self.device_address, reg)
    def read_word(self, reg):
        """ Read a word from the bus """
        return self.byte_swap(self.bus.read_word_data(self.device_address, reg))
    def write_word(self, reg, value):
        """ Write a word to the bus """
        return self.bus.write_word_data(self.device_address, reg, self.byte_swap(value))
    def get_temperature(self):
        """ Get the temperature
        """
        val = self.read_word(TMP75B_REG_TEMP)
        if DEBUG:
            print("DEBUG: raw temperature = {:04x}".format(val))

        # Mask off the integer part of the temperature
        int_part = (val & 0x7F00) >> 8

        # Mask of the fractional part and convert to decimal
        dec_part = ((val & 0x00F0) >> 4) / 16

        # Add to get final temperature and calcualte the sign
        temp = int_part + dec_part
        if val & 0x8000:
            temp *= -1
        return temp
    def print_config(self):
        # pylint: disable=too-many-branches
        """ Print out the configuration """
        val = self.read_word(TMP75B_REG_CONF)

        print("\nTMP75B CONFIGURATION:")

        print("    Config value = {:04x}".format(val))

        cr_mode = val & TMP75B_CFG_CR
        fq_mode = val & TMP75B_CFG_FQ
        pol_mode = val & TMP75B_CFG_POL
        tm_mode = val & TMP75B_CFG_TM
        sd_mode = val & TMP75B_CFG_SD

        if cr_mode == TMP75B_CFG_CR_37:
            my_string = "37Hz (default)"
        elif cr_mode == TMP75B_CFG_CR_18:
            my_string = '18Hz'
        elif cr_mode == TMP75B_CFG_CR_09:
            my_string = '9Hz'
        elif cr_mode == TMP75B_CFG_CR_04:
            my_string = '4Hz'
        else:
            my_string = '    ERROR: Rate not found'
            sys.exit()
        print("    Conversion Rate = {}".format(my_string))

        if fq_mode == TMP75B_CFG_FQ_01:
            my_string = "1 fault (default)"
        elif fq_mode == TMP75B_CFG_FQ_02:
            my_string = "2 faults"
        elif fq_mode == TMP75B_CFG_FQ_04:
            my_string = "4 faults"
        elif fq_mode == TMP75B_CFG_FQ_06:
            my_string = "6 faults"
        print("    Fault Queue to trigger the ALERT pin = {}".format(my_string))

        if pol_mode:
            print("    ALERT is active high")
        else:
            print("    ALERT is active low (default)")

        if tm_mode:
            print("    ALERT is in interrupt mode")
        else:
            print("    ALERT is in comparator mode (default)")

        if sd_mode:
            print("    Device is in shutdown mode")
        else:
            print("    Device is in continuous conversion mode (default)")

        print()

    def reset_config(self):
        """ Reset the configuration """
        return self.write_word(TMP75B_REG_CONF, TMP75B_RESET_CONFIG)
    def set_conversion_rate(self, conversion_rate):
        """ Set the conversion rate """
        if not conversion_rate in [TMP75B_CFG_CR_04,
                                   TMP75B_CFG_CR_09,
                                   TMP75B_CFG_CR_18,
                                   TMP75B_CFG_CR_37]:
            print("ERROR: Invalid Value. Conversion rate not changed.")
            return False

        config = self.read_word(TMP75B_REG_CONF)
        masked_config = config & ~TMP75B_CFG_CR
        new_config = (masked_config | conversion_rate)
        self.write_word(TMP75B_REG_CONF, new_config)
        return True
    def set_fault_queue_trigger(self, fault_queue_trigger):
        """ Set the fault queue trigger """
        if not fault_queue_trigger in [TMP75B_CFG_FQ_01,
                                       TMP75B_CFG_FQ_02,
                                       TMP75B_CFG_FQ_04,
                                       TMP75B_CFG_FQ_06]:
            print("ERROR: Invalid Value. Fault queue trigger not changed.")
            return False
        config = self.read_word(TMP75B_REG_CONF)
        print("{:04x}".format(config))
        masked_config = config & ~TMP75B_CFG_FQ
        print("{:04x}".format(masked_config))
        new_config = (masked_config | fault_queue_trigger)
        print("{:04x}".format(new_config))
        self.write_word(TMP75B_REG_CONF, new_config)
        return True
    def set_alert_polarity(self, alert_polarity):
        """ Set the alert polarity """
        if not alert_polarity in [True, False]:
            print("ERROR: Invalid Value.  Alert polarity not changed.")
            return False
        if alert_polarity:
            new_config = self.read_word(TMP75B_REG_CONF) | TMP75B_CFG_POL
        else:
            new_config = self.read_word(TMP75B_REG_CONF) & ~TMP75B_CFG_POL
        self.write_word(TMP75B_REG_CONF, new_config)
        return True
    def set_alert_mode(self, alert_mode):
        """ Set alert mode """
        if not alert_mode in [True, False]:
            print("ERROR: Invalid Value.  Alert mode not changed.")
            return False
        if alert_mode:
            new_config = self.read_word(TMP75B_REG_CONF) | TMP75B_CFG_TM
        else:
            new_config = self.read_word(TMP75B_REG_CONF) & ~TMP75B_CFG_TM
        self.write_word(TMP75B_REG_CONF, new_config)
        return True
    def set_sd_mode(self, mode):
        """ Set the shutdown mode """
        if not mode in [True, False]:
            print("ERROR: Invalid Value.  Shutdown mode not changed.")
            return False
        if mode:
            new_config = self.read_word(TMP75B_REG_CONF) | TMP75B_CFG_SD
        else:
            new_config = self.read_word(TMP75B_REG_CONF) & ~TMP75B_CFG_SD
        self.write_word(TMP75B_REG_CONF, new_config)
        return True
    def do_one_shot(self):
        """ Setup oneshot """
        new_config = self.read_word(TMP75B_REG_CONF) | TMP75B_CFG_OS
        self.write_word(TMP75B_REG_CONF, new_config)
        time.sleep(0.5)

def main():
    """ Main Program """
    sensor = TMP75B(BUS_ADDRESS, DEV_ADDRESS)
    sensor.print_config()

    sensor.set_sd_mode(True)
    sensor.print_config()

    print(sensor.get_temperature())

    for _ in range(5):
        time.sleep(5)
        print(sensor.get_temperature())

    sensor.set_sd_mode(True)
    sensor.do_one_shot()
    print(sensor.get_temperature())

if __name__ == "__main__":
    main()
