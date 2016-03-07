'''
Created on 18 Jan 2016

@author: keith

Light Levels - Read light level sensor.  

-i integrationTime. 13ms, 101ms or 402ms. Usage example, -i 13
-g integrationGain. 1x or 16x. Usage example, -g 16
-d duration. How long to run this script for in seconds.
-p period. How often to take a reading in seconds.
           Default (if not specified) is to read as fast as possible.
           Rate is limited by how fast we can read the I2C bus and the integration time.

'''
import time
import getopt,sys
import sensor_TSL2561 as TSL5661

TAG = 'myMeasurement'

params = {'integrationTime':'402ms',
          'integrationGain':'16x',
          'duration':0,     # Duration to run the script for in seconds. Default=0 i.e. one run only.
          'period':0.1}     # Frequency of readings in seconds

TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

def getArgs(myParams):
    """
    """    
    helpString = '\n' + __file__ + '\n\n' +\
                 '-h show help\r\n' +\
                 '-i integrationTime. 13ms,101ms or 402ms. Usage -i 13\r\n' + \
                 '-g integrationGain. 1x or 16x. Usage example, -g 16\r\n' +\
                 '-d duration. How long to run this script for in seconds.\r\n' +\
                 '-p period. How often to take a reading in seconds.\r\n'+\
                 '           Default (if not specified) is to read as fast as possible.\r\n'+\
                 '           Rate is limited by how fast we can read the I2C bus and the integration time.'
    
    # First arg is the pathname for the current file
    # Remaining args are those provided on the command line    
    try:
        options,_ = getopt.getopt(sys.argv[1:],"hi:g:d:p:")

    except Exception as e:
        print(e)
        print('\n*** INVALID OPTIONS')
        print(helpString)
        exit()
    
    for opt,arg in options:
        if opt=='-h':
            print(helpString)
            exit()
        elif opt=='-i':
            if arg in ('13','101','402'):
                myParams['integrationTime']=arg+'ms'
            else:
                print(helpString)
                exit()
        elif opt=='-g':
            if arg in ('1','16'):
                myParams['integrationGain']=arg+'x'
            else:
                print(helpString)
                exit()
        elif opt=='-d':
            myParams['duration']=int(arg)
        elif opt=='-p':
            myParams['period']=float(arg)
    
    return myParams
def readSensor(sensor):
    """ Read the sensor and return the measured values
    
    """    
    # Get the readings
    lux, fullScaled, irScaled = sensor.getLux()
    ts = time.time()   
    results=({'location':TAG,
              'full':fullScaled,
              'ir':irScaled,
              'lux':lux,
              'gain':sensor.gain,
              'integrationTime':sensor.integrationTime,
              'timestamp':ts})
    
    return results
    
def main(params):
    
    sensor = TSL5661.tsl2561(integration='13ms')
    
    startTime=time.time()
    while time.time() <= startTime + params['duration']:
        results=readSensor(sensor)
        print(results)
        time.sleep(params['period'])      
            
if __name__ == "__main__":
    
    params = getArgs(params)
    print("INTEGRATION TIME: {}".format(params['integrationTime']))
    print("INTEGRATION GAIN: {}".format(params['integrationGain']))
    print("DURATION        : {}".format(params['duration']))
    print("PERIOD          : {}".format(params['period']))
    
    main(params)