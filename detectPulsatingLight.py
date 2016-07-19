'''
Created on 19 Jul 2016

@author: keith

Test to try and recreate pulsating LED bulb

Soak at 70% for 30mins and then switch to off or 100% for some time.
Repeat while measuring max min levels

'''
import loggingConfig as config
import threadedSerial as AT
import sensor_TSL2561 as TSL5661
import time
import datetime

TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

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
    # Setup the bulb
    AT.startSerialThreads(config.PORT,config.BAUD,printStatus=False,rxQ=True,listenerQ=False)
    nodeId=config.nodeList[0]['node']
    epId=config.nodeList[0]['ep1']
    
    level = 100 # Light level as percentage
    setLevel(nodeId,epId,level)
    time.sleep(5)
    
    # Setup the sensor
    sensor = TSL5661.tsl2561(gain='16x',integration='402ms')
    
    while True:
        """ Soak at 70% for 30mins """

        # Set level
        setLevel(nodeId,epId,70)
        time.sleep(5)
        
        # Inital read
        lux, _, _ = sensor.getLux()
        
        maxLux=lux 
        minLux=lux
        delta=0
        
        # Loop until timeout
        timeout = time.time() + 30*60
        while time.time()<timeout:
            lux, _, _ = sensor.getLux()
            if lux<minLux: minLux=lux 
            if lux>maxLux: maxLux=lux 
            newDelta = maxLux-minLux
            if newDelta!=delta:
                ts=datetime.datetime.now().strftime(TIME_FORMAT)
                print("{}, Delta={}".format(ts,delta))
        
        # Change to 100% for 10mins
        setLevel(nodeId,epId,level)
    
    lux, fullScaled, irScaled = sensor.getLux()
        
    print(lux,fullScaled,irScaled)
    
    return
    
if __name__== "__main__":
    main()
    print('All done.')