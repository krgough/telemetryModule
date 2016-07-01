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

def setLevel(bulbAddress,bulbEp,level,duration):
    """
    """
    hexLevel = "{:02x}".format(int(level/100*254))
    nodeId=config.nodeList[0]['node']
    epId=config.nodeList[0]['ep1']
    respState, respCode, respValue=AT.moveToLevel(nodeId,epId,hexLevel,duration)
    if not respState:
        print("ERROR: moveToLevel has failed. {}".format(respCode,respValue))
        exit()
    return
def main():
    AT.startSerialThreads(config.PORT, config.BAUD, printStatus=False)
    startPercent=10
    stopPercent=100
    stepSize=10

    for level in range(startPercent,stopPercent+stepSize,stepSize):
        duration=0 # Bulb to switch levels as fast as possible
        setLevel(config.nodeId,config.epId, level, duration)
        
        # Now read and print the levels for 1 min
        rll.TAG="{}%".format(level)
        rll.main(rll.params)
        
    return
    
if __name__== "__main__":
    main()
    print('All done.')