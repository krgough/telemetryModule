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
def main():
    """ Read the sensors and then post results to SQL server
    
    """    
    # Create a sensor object
    tsl = TSL5661.tsl2561()
    
    # Get the readings
    lux, fullScaled, irScaled = tsl.lux(full, ir, tsl.gain, tsl.integrationTime)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")    
    results=({'location':location,
              'full':full,
              'ir':ir,
              'lux':lux,
              'gain':tsl.gain,
              'integrationTime':tsl.integrationTime,
              'timestamp':ts})
    
    print(results)
    
    # Post to the AWS SQL server
    postResults(results)

if __name__ == "__main__":
    main()