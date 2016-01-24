'''
Created on 11 Jan 2016

@author: keith

TSL2561 Light Sensor - Read the TSL2561 lux sensor

Default device address for adafruit board is 0x39

'''
import smbus
import time

package_reg = 0x11 # Package
device_reg  = 0x12 #
address = 0x39
busAddress = 1 # Change to 0 for older RPi revision

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
TSL2561_402MS_FULL_SCALE = 65536

# Lux Calculations coefficients
LUX_A1 = 0.0304
LUX_B1 = 0.062
LUX_A2 = 0.0224
LUX_B2 = 0.031
LUX_A3 = 0.0128
LUX_B3 = 0.0153
LUX_A4 = 0.00146
LUX_B4 = 0.00112

#TODO: Change inttime and gain to use dict
#TODO: Put lookup in setters to check for valid values

class tsl2561(object):
    def __init__(self,
                 busAddress = busAddress,
                 sensorAddress = address,
                 integration = '402ms',
                 gain = '16x'):

        self.bus = smbus.SMBus(busAddress)
        self.sensorAddress = address
        self.sensorError = None
        
        # Check device is present by reading the ID register
        val = self.getRegister(TSL2561_REG_ID)
        self.id = val
        if not (val & 0x50):
            print("ERROR: Device ID should be 0x50.")
            return

        self._gain = gain
        self._integrationTime = integration
        self.setGainAndIntegration()
        self.disable()

    @ property
    def gain(self):
        return self._gain
    @ property
    def integrationTime(self):
        return self._integrationTime
    
    @ gain.setter
    def gain(self,gainValue):
        # Check we are trying to set a valid value
        if not gainValue in list(TSL2561_GAIN_VALS.keys()):
            print("ERROR: Invalide gain value. {} is not in {}".format(gainValue,list(TSL2561_GAIN_VALS.keys())))
            return
        # If ok the set the value
        self._gain=gainValue
        self.setGainAndIntegration()
    @ integrationTime.setter
    def integrationTime(self,integrationTimeValue):
        # Check we are trying to set a valid value
        if not integrationTimeValue in list(TSL2561_INT_VALS.keys()):
            print("ERROR: Invalid integration time value. {} is not in {}.".format(integrationTimeValue,
                                                                                   list(TSL2561_INT_VALS.keys())))
        # If ok then set the value
        self._integrationTime=integrationTimeValue
        self.setGainAndIntegration()

    def getRegister(self,reg):
        val = self.bus.read_byte_data(
            address,
            TSL2561_CMD_BIT | reg)
        return val
    def enable(self):
        """
        """
        self.bus.write_byte_data(
            address,
            TSL2561_CMD_BIT | TSL2561_REG_CONTROL,
            TSL2561_CTRL_POWER_ON)
        return
    def disable(self):
        """
        """
        self.bus.write_byte_data(
            address,
            TSL2561_CMD_BIT | TSL2561_REG_CONTROL,
            TSL2561_CTRL_POWER_OFF)
        return
    def setGainAndIntegration(self):
        """ Sets the timing register to the gain and integrationTime settings
        
        """
        gainVal = TSL2561_GAIN_VALS[self._gain]
        intVal = TSL2561_INT_VALS[self._integrationTime]
        
        self.bus.write_byte_data(
            self.sensorAddress,
            TSL2561_CMD_BIT | TSL2561_REG_TIMING,
            gainVal | intVal)
        return
    def getRawLuminosity(self):
        """
        """
        #Turn on sensor
        self.enable()
        
        # Wait for integration to complete
        if self._integrationTime=='13ms':
            time.sleep(0.050)
        elif self._integrationTime=='101ms':
            time.sleep(0.150)
        elif self._integrationTime=='402ms':
            time.sleep(0.450)
        
        full = self.bus.read_word_data(
            self.sensorAddress,
            TSL2561_CMD_BIT | TSL2561_CMD_WORD | TSL2561_REG_DATA0_LOW)
        ir = self.bus.read_word_data(
            self.sensorAddress,
            TSL2561_CMD_BIT | TSL2561_CMD_WORD | TSL2561_REG_DATA1_LOW)

        # Turn off sensor
        self.disable()
        return full,ir
    def getRawLuminosityAutoGain(self):
        """ Automatically adjusts gain to prevent saturation
            
            Start with full gain then select full gain if reading is over the threshold
            for the given integrationTime
        
        """
        
        # Set max gain and get a reading
        self.gain = '16x'
        full,ir = self.getRawLuminosity()
        
        if self._integrationTime == '13ms':
            threshold = TSL2561_13MS_FULL_SCALE * 0.96
        elif self._integrationTime == '101ms':
            threshold = TSL2561_101MS_FULL_SCALE * 0.96
        elif self._integrationTime == '402ms':
            threshold = TSL2561_402MS_FULL_SCALE * 0.96
        
        # If reading greater than threshold then reduce gain
        if full>threshold:
            self.gain = '1x'
            full,ir = self.getRawLuminosity()
        
        return full,ir
    def scaleRawReadings(self,full,ir,gain,integrationTime):
        """ Normalise the raw reading by scaling for gain and integrationTime
        
        """
        if integrationTime == '13ms':
            intScale = TSL2561_13MS_SCALE
        if integrationTime == '101ms':
            intScale = TSL2561_101MS_SCALE
        if integrationTime == '402ms':
            intScale = TSL2561_402MS_SCALE
            
        if gain == '1x':
            gainScale = 16
        if gain == '16x':
            gainScale = 1
            
        fullScaled = full * intScale * gainScale
        irScaled = ir * intScale * gainScale
        
        return fullScaled,irScaled
    def luxCalculation(self,full,ir,gain,integrationTime):
        """ Calculate lux
        
            Scale for integration time and gain
            Calculate lux
        
            use -1 as saturated value
            
        """
        # Catch divide by zero
        if irScaled==0: return 0
        
        # Catch saturation
        if integrationTime == '13ms' and full>=TSL2561_13MS_FULL_SCALE:
            return -1
        elif integrationTime == '101ms' and full>=TSL2561_101MS_FULL_SCALE:
            return -1
        elif integrationTime == '402ms' and full>=TSL2561_402MS_FULL_SCALE:
            return -1  
        
        # Scale the raw values
        fullScaled,irScaled = scaleRawReadings(full,ir,gain,integrationTime)        
        
        # Calculate the lux ratio
        ratio = irScaled/fullScaled
        #print(ratio)
        
        # Calculate lux
        if ratio<= 0.5:
            lux = (LUX_A1*fullScaled)-(LUX_A1*fullScaled*ratio**1.4)
        elif ratio<=0.61:
            lux = (LUX_A2*fullScaled)-(LUX_B2*irScaled)
        elif ratio<=0.8:
            lux = (LUX_A3*fullScaled)-(LUX_B3*irScaled)
        elif ratio<=1.3:
            lux = (LUX_A4*fullScaled)-(LUX_B4*irScaled)
        elif ratio>1.3:
            lux = 0
         
        lux = round(lux)
        return lux
    
    ''' Use these methods to get the Luminosity readings and/or Lux value'''
    def getScaledLuminosity(self,autoGain=True):
        """ Get luminosity values scaled for gain and integration time.
        
        """
        if autoGain:
            full,ir = getRawLuminosityAutoGain()
        else:
            full,ir = getRawLuminosity()
        
        fullScaled,irScaled = scaleRawReadings(full,ir,self.gain,self.integrationTime)
        return fullScaled,irScaled
    def getLux(self,autoGain=True):
        """ Get lux value
        
        """
        if autoGain:
            full,ir = getRawLuminosityAutoGain()
        else:
            full,ir = getRawLuminosity()
        
        lux = luxCalculation(full,ir,self.gain,self.integrationTime)
        return lux
        
if __name__ == "__main__":
    tsl = tsl2561()
    print("DeviceID: {}".format(hex(tsl.id)))

    full,ir = tsl.getRawLuminosity()
    fullScaled,irScaled = tsl.scaleRawReadings(full,ir,tsl.gain,tsl.integrationTime)
    lux = tsl.luxCalculation(full,ir,tsl.gain,tsl.integrationTime)
    print("\nGain=16x. Full 402ms Integration time (max resolution)")
    print("RAW READINGS:    Full={}, IR={}".format(full,ir))
    print("SCALED READINGS: Full={}, IR={}".format(fullScaled,irScaled))
    print("LUX = {}".format(lux))
    
    tsl.gain = '1x'
    full,ir = tsl.getRawLuminosity()
    fullScaled,irScaled = tsl.scaleRawReadings(full,ir,tsl.gain,tsl.integrationTime)
    lux = tsl.luxCalculation(full,ir,tsl.gain,tsl.integrationTime)    
    print("\nGain=1x.  Full 402ms Integration Time (max resolution)")
    print("RAW READINGS:    Full={}, IR={}.".format(full,ir))
    print("SCALED READINGS: Full={}, IR={}".format(fullScaled,irScaled))
    print("LUX = {}".format(lux))
    
    # Now use auto gain
    full,ir = tsl.getLuminosityAutoGain()
    fullScaled,irScaled = tsl.scaleRawReadings(full,ir,tsl.gain,tsl.integrationTime)
    lux = tsl.luxCalculation(full,ir,tsl.gain,tsl.integrationTime)      
    print("\nAGC {} Gain selected.  402ms Integration Time (max resolution)".format(tsl.gain))
    print("RAW READINGS:    Full={}, IR={}.".format(full,ir))
    print("SCALED READINGS: Full={}, IR={}".format(fullScaled,irScaled))
    print("LUX = {}".format(lux))
    
    # Use the recommended methods
    fullScaled,irScaled = tsl.getScaledLuminosity()
    lux = tsl.getLux
    print("\nSCALED READINGS: Full={}, IR={}".format(fullScaled,irScaled))
    print("LUX = {}".format(lux))
        
    print('\nAll Done')