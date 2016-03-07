'''
Created on 7 Mar 2016

@author: keith

Measure the LUX output for given illumination levels.

Loop for given number of steps:
    - Set the wanted level
    - Measure Lux for 1min
    - Results printed to console so redirect to file is advisable

'''
import loggingConfig as config
import threadedSerial as AT
import readLightLevels as rll

MAX_LEVEL = 255 #
BULB_ADDRESS = 'C7F0'
BULB_EP = '01'

def buildLevelValues(percentageStepSize,maxLevel):
    """ Returns a list of hex values
    """
    myList = []
    for l in range(0,100,percentageStepSize):
        l = l+percentageStepSize
        level = int(l/100 * 255)
        levelHex = "{:0x}".format(level)
        #print(l,level,levelHex)
        myList.append(levelHex)
    
    return myList
def setLevel(bulbAddress,bulbEp,level,duration):
    """
    """
    respState, respCode, respValue=AT.moveToLevel(bulbAddress, bulbEp, level, duration)
    if not respState:
        print("ERROR: moveToLevel has failed. {}".format(respCode,respValue))
        exit()
    return
def main():
    AT.startSerialThreads(config.PORT, config.BAUD, printStatus=False)
    levels = buildLevelValues(10, MAX_LEVEL)

    for level in levels:
        duration=0 # Bulb to switch levels as fast as possible
        setLevel(BULB_ADDRESS,BULB_EP, level, duration)
        
        # Now read the levels for 1 min
        rll.main(rll.params,level)
        
    return
    
if __name__== "__main__":
    main()
    print('All done.')