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

# Channels
TSL2561_FULLSPECTRUM = 0x00   # Channel 0
TSL2561_INFRARED     = 0x01   # Channel 1
TSL2561_VISIBLE      = 0x02   # Channel 0 - Channel 1

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
TSL2561_TIMING_GAIN_1X  = 0x00 
TSL2561_TIMING_GAIN_16X = 0x10
TSL2561_TIMING_13MS  = 0x00  # 13.7ms
TSL2561_TIMING_101MS = 0x01  # 101ms
TSL2561_TIMING_402MS = 0x02  # 402ms

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

class tsl2561(object):
    def __init__(self,
                 busAddress = busAddress,
                 sensorAddress = address,
                 integration = TSL2561_TIMING_402MS,
                 gain = TSL2561_TIMING_GAIN_16X):

        self.bus = smbus.SMBus(busAddress)
        self.sensorAddress = address
        
        # Check device is present by reading the ID register
        val = self.getRegister(TSL2561_REG_ID)
        self.id = val
        if not (val & 0x50):
            print("ERROR: Device ID should be 0x50.")
            return

        self.setGainAndIntegration(gain,integration)
        self.disable()

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
    def setGainAndIntegration(self,gain,integrationTime):
        """
        """
        self._gain=gain
        self._integrationTime=integrationTime

        self.bus.write_byte_data(
            self.sensorAddress,
            TSL2561_CMD_BIT | TSL2561_REG_TIMING,
            self._gain | self._integrationTime)
        return
    def getFullLuminosity(self):
        """
        """
        #Turn on sensor
        self.enable()
        
        # Wait for integration to complete
        if self._integrationTime==TSL2561_TIMING_13MS:
            time.sleep(0.050)
        elif self._integrationTime==TSL2561_TIMING_101MS:
            time.sleep(0.150)
        elif self._integrationTime==TSL2561_TIMING_402MS:
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
    def getLuminosityAutoGain(self):
        """ Automatically adjusts gain to prevent saturation
            
            Start with full gain then select full gain if reading is over the threshold
            for the given integrationTime
        
        """
        
        # Set max gain and get a reading
        self.setGainAndIntegration(TSL2561_TIMING_GAIN_16X,self._integrationTime)
        full,ir = self.getFullLuminosity()
        
        if self._integrationTime == TSL2561_TIMING_13MS:
            threshold = TSL2561_13MS_FULL_SCALE * 0.96
        elif self._integrationTime == TSL2561_TIMING_101MS:
            threshold = TSL2561_101MS_FULL_SCALE * 0.96
        elif self._integrationTime == TSL2561_TIMING_402MS:
            threshold = TSL2561_402MS_FULL_SCALE*0.96
        
        # If reading greater than threshold then reduce gain
        if full>threshold:
            self.setGainAndIntegration(TSL2561_TIMING_GAIN_1X,self._integrationTime)
            full,ir = self.getFullLuminosity()
        
        return full,ir
    
    def lux(self,full,ir,gain,integrationTime):
        """ Calculate lux
        
            Scale for integration value
            Scale for gain
            Calculate lux
        
        """
        if integrationTime == TSL2561_TIMING_13MS:
            intScale = TSL2561_13MS_SCALE
        if integrationTime == TSL2561_TIMING_101MS:
            intScale = TSL2561_101MS_SCALE
        if integrationTime == TSL2561_TIMING_402MS:
            intScale = TSL2561_402MS_SCALE
            
        if gain == TSL2561_TIMING_GAIN_1X:
            gainScale = 16
        if gain == TSL2561_TIMING_GAIN_16X:
            gainScale = 1
            
        full = full * intScale * gainScale
        ir = ir * intScale * gainScale

        if ir==0: return 0
        
        ratio = ir/full
        print(ratio)
        
        if ratio<= 0.5:
            lux = (LUX_A1*full)-(LUX_A1*full*ratio**1.4)
        elif ratio<=0.61:
            lux = (LUX_A2*full)-(LUX_B2*ir)
        elif ratio<=0.8:
            lux = (LUX_A3*full)-(LUX_B3*ir)
        elif ratio<=1.3:
            lux = (LUX_A4*full)-(LUX_B4*ir)
        elif ratio>1.3:
            lux = 0
            
        return lux
        
if __name__ == "__main__":
    tsl = tsl2561()
    print("DeviceID: {}".format(hex(tsl.id)))

    full,ir = tsl.getFullLuminosity()
    print()
    print("READINGS: Full={}, IR={}. Gain=16x integration=402ms".format(full,ir))
    print("LUX = {}".format(tsl.lux(full,ir,tsl._gain,tsl._integrationTime)))
    
    tsl.setGainAndIntegration(TSL2561_TIMING_GAIN_1X,TSL2561_TIMING_402MS)
    full,ir = tsl.getFullLuminosity()
    print()
    print("READINGS: Full={}, IR={}. Gain=1x, integration=402ms".format(full,ir))
    print("LUX = {}".format(tsl.lux(full,ir,tsl._gain,tsl._integrationTime)))
    
    # Now use auto gain
    full,ir = tsl.getLuminosityAutoGain()
    
    if tsl._gain==TSL2561_TIMING_GAIN_1X:
        gain='1x'
    else:
        gain='16x'
    
    print("\nNow with automatic gain control")
    print("READINGS: Full={}, IR={}. Gain={}, integration=402ms".format(full,ir,gain))
    print("LUX = {}".format(tsl.lux(full,ir,tsl._gain,tsl._integrationTime)))
    print('All Done')