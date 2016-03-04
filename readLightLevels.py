'''
Created on 18 Jan 2016

@author: keith

Light Levels - Read light level sensor and post results to AWS SQL server.

sql database: illumination
sql Table name: lightlevels

sql Table Column names:
location,     full , ir   , lux  , gain        , integrationTime, timestamp
charvar(255), int(), int(), int(), charvar(255), charvar(255)   , datetime()

Cron job will run script every 2mins
Read sensor
Write values to sql_server on aws server

'''
import time
import sensor_TSL2561 as TSL5661
import peeweeModule as pw

location = 'upstairsOffice'
database = 'illumination'
table = 'lightLevels'

def postResults(results):
    """ Insert the results into the mySQL database on the server
    
    """
    #for r in results:
    #    sql.insertNewEntry(sqlCreds, table, r)
    pw.insertRows(pw.db_Hotwater, pw.temperature, results)
    return
def readSensor(sensor):
    """ Read the sensors and then post results to SQL server
    
    """    
    # Get the readings
    lux, fullScaled, irScaled = sensor.getLux()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")    
    results=({'location':location,
              'full':fullScaled,
              'ir':irScaled,
              'lux':lux,
              'gain':sensor.gain,
              'integrationTime':sensor.integrationTime,
              'timestamp':ts})
    
    print(results)
    
    # Post to the AWS SQL server
    postResults(results)
    return results
    
def main():
    sensor = TSL5661.tsl2561(integration='13ms')
    readContinuous=True
    if readContinuous==True:
        while True:
            results=readSensor(sensor)
            print(results)
            time.sleep(0.1)
    
    results = readSensor(sensor)
    print(results)       
    postResults(results)
            
if __name__ == "__main__":
    main()