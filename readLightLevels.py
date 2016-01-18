'''
Created on 18 Jan 2016

@author: keith

Light Levels - Read light level sensor and post results to AWS SQL server.

sql Table name: light_TSL2561

sql Table Column names:
full,ir,lux,gain,integration,timestamp

{sensorID:id, sensorName:name, temperature:temp, timeStamp:time}

Cron job will run script every 2mins
Read all sensors
Write values to sql_server on aws server

'''
import time
#import mySQL_Library as sql
import sensor_TSL2561 as TSL5661
import peeweeModule as pw

user = 'keith.gough'
database = 'lightMeasurements'
table = 'light'

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
    debug = False
    
    # Create a sensor object
    tsl = TSL5661.tsl2561()
    
    if debug: print(devIds)
    
    results=[]
    ts = time.strftime("%Y-%m-%d %H:%M:%S")    

    
    results.append({'username':user,'sensorId':d,'temperature':temp,'statusCode':status,'sensorName':sensorName,'timestamp':ts})
    
    # Post to the AWS SQL server
    postResults(results)
    
    for r in results:
        print(r)

if __name__ == "__main__":
    main()