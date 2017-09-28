'''
Created on 7 Mar 2016

@author: keith

Measure the LUX output for given illumination levels.

Loop for given number of steps:
    - Set the wanted level
    - Measure Lux for 1min
    - Results printed to console so redirect to file is advisable

'''

import apiMethods as api
import apiConfig
import time
import sensor_TSL2561 as TSL2561

nodeName='Sitt Colour'

def main():
    
    username=apiConfig.username
    password=apiConfig.password
    url=apiConfig.url
    acct = api.sessionObject(username,password,url)
    
    startPercent=1
    stopPercent=100
    stepSize=1
    
    tsl = TSL2561.tsl2561()
    autoGain=False
    gain='1x'
    intTime='402ms'
    
    for level in range(startPercent,stopPercent+stepSize,stepSize):
        
        r,success,payload=acct.setBrightness(nodeName, level)
        if not success:
            print("API problem: {},{},{}".format(r,success,payload))
            exit()
            
        time.sleep(2)
        
        # Now read and print the levels for 1 min
        lux, fullScaled, irScaled = tsl.getLux(autoGain, gain, intTime)
        print("{},{},{},{}".format(level,lux,fullScaled,irScaled))
        
    return
    
if __name__== "__main__":
    main()
    print('All done.')