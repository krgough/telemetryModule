'''
Created on 1 Jul 2016

@author: keith

Measure the LUX output for a given illumination levels.
Soak for some extended period
Results printed to console so redirect to file is advisable

'''
import loggingConfig as config
import threadedSerial as AT
import readLightLevels as rll

LEVEL = 70 # Light level as percentage

def setLevel(bulbAddress,bulbEp,level,duration):
    """
    """
    level = "{:02x}".format(int(level/100*254))
    
    respState, respCode, respValue=AT.moveToLevel(bulbAddress, bulbEp, level, duration)
    if not respState:
        print("ERROR: moveToLevel has failed. {}".format(respCode,respValue))
        exit()
    return
def main():
    AT.startSerialThreads(config.PORT, config.BAUD, printStatus=False)

    duration=0 # Bulb to switch levels as fast as possible
    setLevel(config.nodeId,config.epId,LEVEL,duration)
        
    # Now read and print the levels for 1 min
    rll.TAG="{}%".format(LEVEL)
    rll.params['duration'] = 60*60*2  # 2 hours
    rll.params['period'] = 1          # 1 second
    rll.main(rll.params)
    
    return
    
if __name__== "__main__":
    main()
    print('All done.')