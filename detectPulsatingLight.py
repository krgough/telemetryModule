'''
Created on 19 Jul 2016

@author: keith

Test to try and recreate pulsating LED bulb

Soak at 70% for 30mins and then switch to off or 100% for some time.
Repeat while measuring max min levels

'''
import loggingConfig as config
import threadedSerial as AT
import readLightLevels as rll
import sensor_TSL2561 as TSL5661

def setLevel(nodeId,epId,level):
    """
    """
    level = "{:02x}".format(int(level/100*254))
    
    respState, respCode, respValue=AT.moveToLevel(nodeId,epId,myLevel=level)
    if not respState:
        print("ERROR: moveToLevel has failed. {}".format(respCode,respValue))
        exit()
    return
def main():
    AT.startSerialThreads(config.PORT,config.BAUD,printStatus=False,rxQ=True,listenerQ=False)

    nodeId=config.nodeList[0]['node']
    epId=config.nodeList[0]['ep1']
    
    level = 70 # Light level as percentage
    setLevel(nodeId,epId,level)
        
    sensor = TSL5661.tsl2561(gain='16x',integration='402ms')    
    lux, fullScaled, irScaled = sensor.getLux()
        
    print(lux,fullScaled,irScaled)
    
    return
    
if __name__== "__main__":
    main()
    print('All done.')