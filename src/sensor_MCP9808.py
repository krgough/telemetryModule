'''
Created on 16 Jan 2016

@author: keith

MCP9808 temperature sensor library
High accuracy I2C temperature sensor

Default I2C address is 0x18
Temperature register in 0x05
    2 Bytes
    Bit15, Bit14, Bit13, Bit12, Bit11, Bit10, Bit09, Bit08
    n/a    n/a    n/a    Sign   2^7'C  2^6'C  2^5'C  2^4'C

    Bit07, Bit06, Bit05, Bit04, Bit03, Bit02, Bit01, Bit00
    2^3'C  2^2'C  2^1'C  2^0'C  2^-1'C 2^-2'C 2^-3'C 2^-4'C

    Temperatures are represented in 2s Complement therefore conversion
    is as follows...

    Read MSB & LSB
    With MSB determine sign of reading and mask off upper bits.
    Shift the 4 reading bits 8 positions to the left
    LSB bits are already in correct position so now add the bytes together
    e.g.   MSB = 0000ABCD 00000000
           LSB =          EFGHIJKL

           SUM = 0000ABCD EFGHIJKL

    Lower 4 bits are fractions so we need to shift the result 4 bits to the
    right (or actually divide by 16 in a float)

    We then need to subtract that value from 256 (2^8) if the reading is a
    negative reading.

'''
import smbus2  # @UnresolvedImport
import time

t_reg = 0x05
address = 0x18
busAddress = 1 # Change to 0 for older RPi revision
bus = smbus2.SMBus(busAddress)

def getTemperature():
    """
    """
    # Read 2 bytes and then swap the upper and lower bytes
    t = bus.read_word_data(address,t_reg)
    u = (t & 0x000F) << 8
    l = (t & 0xFF00) >> 8
    result = (u+l)/16

    # If temp is negative then convert from 2s complement
    if t & 0x0010:
        result -= 256

    return result

def getTempetature_old():
    reading = bus.read_i2c_block_data(address, t_reg)
    t = (reading[0] << 8) + reading[1]

    # calculate temperature (see 5.1.3.1 in datasheet)
    temp = t & 0x0FFF
    temp /=  16.0

    # If temp is negative then convert from 2s complement
    if (t & 0x1000): temp -= 256

    return temp

if __name__ == "__main__":
    while True:
        print(getTemperature())
        time.sleep(1)
    print('All Done')