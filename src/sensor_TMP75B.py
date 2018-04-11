'''
Created on 13 Mar 2018

@author: Keith.Gough

TMP75B I2C Temperature Sensor 

'''

import smbus2
import time

# Address values
BUS_ADDRESS = 0x01   # I2C 1 on rPi
DEV_ADDRESS = 0x48   # Address for the tmp75b IC

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

debug = False

class tmp75b(object):
    def __init__(self, busAddress, deviceAddress):
        self.busAddress = busAddress
        self.deviceAddress = deviceAddress
        
        self.bus = smbus2.SMBus(self.busAddress)
        
        # Check if device is present by reading the config reg
        val = self.readWord(TMP75B_REG_CONF)
        if (val & 0x00FF) != 0x00FF :
            print("ERROR: Device not found at adddress {}".format(self.deviceAddress))
            print("{:04x}".format(val))
            exit()
        
        # Do a reset
        self.resetConfig()
    
    def byteSwap(self,val):
        lb = (0xff00 & val) >> 8
        ub = (0x00ff & val) << 8
        return lb | ub
    def readByte(self,reg):
        return self.bus.read_byte_data(self.deviceAddress,reg)
    def readWord(self,reg):
        return self.byteSwap(self.bus.read_word_data(self.deviceAddress,reg))
    def writeWord(self,reg,value):
        return self.bus.write_word_data(self.deviceAddress, reg, self.byteSwap(value))
    def getTemperature(self):
        """ self.bus.read_word_data(
        """
        val = self.readWord(TMP75B_REG_TEMP)
        if debug: print("DEBUG: raw temperature = {:04x}".format(val))
        
        # Mask off the integer part of the temperature
        intPart = (val & 0x7F00) >> 8
        
        # Mask of the fractional part and convert to decimal
        decPart = ((val & 0x00F0) >> 4) / 16
        
        # Add to get final temperature and calcualte the sign
        temp = intPart + decPart
        if val & 0x8000: temp*=-1
        return temp
    def printConfig(self):
        val = self.readWord(TMP75B_REG_CONF)

        print("\nTMP75B CONFIGURATION:")

        print("    Config value = {:04x}".format(val))
        
        crMode = val & TMP75B_CFG_CR
        fqMode = val & TMP75B_CFG_FQ
        polMode = val & TMP75B_CFG_POL
        tmMode = val & TMP75B_CFG_TM
        sdMode = val & TMP75B_CFG_SD
        
        if crMode==TMP75B_CFG_CR_37:
            myString="37Hz (default)"
        elif crMode==TMP75B_CFG_CR_18:
            myString='18Hz'
        elif crMode==TMP75B_CFG_CR_09:
            myString='9Hz'
        elif crMode==TMP75B_CFG_CR_04:
            myString='4Hz'
        else:
            myString='    ERROR: Rate not found'
            exit()
        print("    Conversion Rate = {}".format(myString))
        
        if fqMode==TMP75B_CFG_FQ_01:
            myString = "1 fault (default)"
        elif fqMode==TMP75B_CFG_FQ_02:
            myString = "2 faults"
        elif fqMode==TMP75B_CFG_FQ_04:
            myString = "4 faults"
        elif fqMode==TMP75B_CFG_FQ_06:
            myString = "6 faults"
        print("    Fault Queue to trigger the ALERT pin = {}".format(myString))
        
        if polMode:
            print("    ALERT is active high")
        else:
            print("    ALERT is active low (default)")
        
        if tmMode:
            print("    ALERT is in interrupt mode")
        else:
            print("    ALERT is in comparator mode (default)")
        
        if sdMode:
            print("    Device is in shutdown mode")
        else:
            print("    Device is in continuous conversion mode (default)")
        
        print()
        return

    def resetConfig(self):
        return self.writeWord(TMP75B_REG_CONF, TMP75B_RESET_CONFIG)
    def setConversionRate(self,conversionRate):
        if not conversionRate in [TMP75B_CFG_CR_04,TMP75B_CFG_CR_09,TMP75B_CFG_CR_18,TMP75B_CFG_CR_37]:
            print("ERROR: Invalid Value. Conversion rate not changed.")
            return False

        config = self.readWord(TMP75B_REG_CONF)
        maskedConfig = config & ~TMP75B_CFG_CR
        newConfig = (maskedConfig | conversionRate)
        self.writeWord(TMP75B_REG_CONF, newConfig)
        return True        
    def setFaultQueueTrigger(self,faultQueueTrigger):
        if not faultQueueTrigger in [TMP75B_CFG_FQ_01,TMP75B_CFG_FQ_02,TMP75B_CFG_FQ_04,TMP75B_CFG_FQ_06]:
            print("ERROR: Invalid Value. Fault queue trigger not changed.")
            return False
        config = self.readWord(TMP75B_REG_CONF)
        print("{:04x}".format(config))
        maskedConfig = config & ~TMP75B_CFG_FQ
        print("{:04x}".format(maskedConfig))
        newConfig = (maskedConfig | faultQueueTrigger)
        print("{:04x}".format(newConfig))
        self.writeWord(TMP75B_REG_CONF, newConfig)
        return True
    def setAlertPolarity(self,alertPolarity):
        if not alertPolarity in [True,False]:
            print("ERROR: Invalid Value.  Alert polarity not changed.")
            return False
        if alertPolarity:
            newConfig = self.readWord(TMP75B_REG_CONF) | TMP75B_CFG_POL
        else:
            newConfig = self.readWord(TMP75B_REG_CONF) & ~TMP75B_CFG_POL
        self.writeWord(TMP75B_REG_CONF, newConfig)
        return True
    def setAlertMode(self,alertMode):
        if not alertMode in [True,False]:
            print("ERROR: Invalid Value.  Alert mode not changed.")
            return False
        if alertMode:
            newConfig = self.readWord(TMP75B_REG_CONF) | TMP75B_CFG_TM
        else:
            newConfig = self.readWord(TMP75B_REG_CONF) & ~TMP75B_CFG_TM
        self.writeWord(TMP75B_REG_CONF, newConfig)
        return True
    def setSdMode(self,mode):
        if not mode in [True,False]:
            print("ERROR: Invalid Value.  Shutdown mode not changed.")
            return False
        if mode:
            newConfig = self.readWord(TMP75B_REG_CONF) | TMP75B_CFG_SD
        else:
            newConfig = self.readWord(TMP75B_REG_CONF) & ~TMP75B_CFG_SD
        self.writeWord(TMP75B_REG_CONF, newConfig)        
        return True
    def doOneShot(self):
        newConfig = self.readWord(TMP75B_REG_CONF) | TMP75B_CFG_OS
        self.writeWord(TMP75B_REG_CONF, newConfig)
        time.sleep(0.5)
        return
    
if __name__=="__main__":
  
    mySensor = tmp75b(BUS_ADDRESS,DEV_ADDRESS)
    mySensor.printConfig()
    
    mySensor.setSdMode(True)
    mySensor.printConfig()
    
    print(mySensor.getTemperature())
    
    for i in range(5):
        time.sleep(5)
        print(mySensor.getTemperature())
        
    mySensor.setSdMode(True)
    mySensor.doOneShot()
    print(mySensor.getTemperature())
    
    