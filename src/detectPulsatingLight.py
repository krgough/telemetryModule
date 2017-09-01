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
import random

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
def soakTest(nodeId,epId,level,soakTime):
    """ Sets the bulb to a given level for a given time and returns the max,min lux levels
        measured during that period.
        
        level is 0-100%
        soakTime is in seconds
        
    """    
    # Light level as percentage
    setLevel(nodeId,epId,level)
    time.sleep(5)
    
    # Setup the sensor
    sensor = TSL5661.tsl2561()
    lux,_,_ = sensor.getLux()
    minLux=lux 
    maxLux=minLux
    
    timeout=time.time()+soakTime
    while time.time() < timeout:
        lux,_,_ = sensor.getLux()
        if lux<minLux: minLux=lux 
        if lux>maxLux: maxLux=lux 
    
    return minLux,maxLux

def main():
    print("*** Pulsating lamp checkGainAndAgc")
    print("Soaking at 70% for 30mins then at a random level for 5mins")
    print("Measure max,mix lux during 30min soak")
    print("Assumption is that we get a larger slow variation but this will not detect the problem")
    print("if the bulb varies normally be the same amount but too quickly to see.")
    
    # Create a results file
    ts=datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    resultFile = '/home/pi/pulsatingBulbResult_{}'.format(ts)
    
    # Setup the bulb
    AT.startSerialThreads(config.PORT,config.BAUD,printStatus=False,rxQ=True,listenerQ=False)
    nodeId=config.nodeList[0]['node']
    epId=config.nodeList[0]['ep1']
    
    print("\nSetting bulb to 100% initially...")
    level = 100 # Light level as percentage
    setLevel(nodeId,epId,level)
    time.sleep(5)
    print("\nStarting iterations...")
    
    for i in range(1,100):
        """ Soak at 70% for 30mins """
        minLux,maxLux=soakTest(nodeId,epId,70,30*60)
        ts=datetime.datetime.now().strftime(TIME_FORMAT)
        myString = "Interation={},{},{},{},{}".format(i,ts,minLux,maxLux,maxLux-minLux)
        print(myString)
        with open(resultFile,'a') as rf:
            print(myString,file=rf)
        
        # Set level to random value for 5mins
        level=random.randint(0,100)
        setLevel(nodeId,epId,level)
        time.sleep(5*50)
        
    return
    
if __name__== "__main__":
    main()
    print('All done.')