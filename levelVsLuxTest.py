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

def setLevel(nodeId,epId,level):
    """
    """
    hexLevel = "{:02x}".format(int(level/100*254))
    respState, respCode, respValue=AT.moveToLevel(nodeId,epId,myLevel=hexLevel)
    if not respState:
        print("ERROR: moveToLevel has failed. {}".format(respCode,respValue))
        exit()
    return
def main():
    AT.startSerialThreads(config.PORT,config.BAUD,printStatus=False,rxQ=True,listenerQ=False)
    startPercent=10
    stopPercent=100
    stepSize=10
    nodeId=config.nodeList[0]['node']
    epId=config.nodeList[0]['ep1']
    
    for level in range(startPercent,stopPercent+stepSize,stepSize):
        setLevel(nodeId,epId, level)
        
        # Now read and print the levels for 1 min
        rll.TAG="{}%".format(level)
        rll.main(rll.params)
        
    return
    
if __name__== "__main__":
    main()
    print('All done.')