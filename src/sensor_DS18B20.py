'''
Created on 16 Jan 2016

@author: keith

DS18B20 Temperature Sensor Library 

One wire data bus sensor.  Multiple sensors on one GPIO.

'''

import os,sys,time

#import mySqlLibrary as sql

nullTemperature = 999
w1_devices = '/sys/bus/w1/devices'

def getDeviceIds():
    """
    """
    myNames = os.listdir(w1_devices)
    ids =[]
    for d in myNames:
        if d.startswith("28-"):
            ids.append(d)

    return ids
def getTemperatureReading(devId):
    """
    """
    try:
        with open("{}/{}/w1_slave".format(w1_devices,devId)) as f:
            myText = f.read()
    
        """
        Reading has the form..
        
        3c 01 4b 46 7f ff 0c 10 36 : crc=36 YES
        3c 01 4b 46 7f ff 0c 10 36 t=19750
        
        check for a 'YES"
        """   
        readOk = True if (myText.find('YES')>0) else False
        
        if readOk:
            myTemperature = int(myText.split("\n")[1].split("=")[1])
            statusCode = 'ReadingOK'
        else:
            myTemperature=nullTemperature
            statusCode = myText
            
    except:
        e = sys.exc_info()[0]
        statusCode=e
        myTemperature=999
        
    return myTemperature,statusCode

if __name__ == "__main__":
    debug = False
    
    devIds = getDeviceIds()
    if debug: print(devIds)
    
    results=[]
    ts = time.strftime("%Y-%m-%d %H:%M:%S")    
    for d in devIds:
        temp,status = getTemperatureReading(d)
        print("{}, {}'C, {}".format(d,temp,status))

    print("All Done.")