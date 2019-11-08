'''
Created on 31 Dec 2015

@author: keith

Hotwater Cylinder - read temperature sensors and post results to AWS SQL server.

Sensor1 = Top of cylinder
Sensor2 =
Sensor3 = 
Sensor4 = 
Sensor5 = Bottom of cylinder

sql Table Column names
sensorId, sensorName, temperature, statusCode, timestamp

sensorLookup = {sensor1:sensorID,
                sensor2:sensorID,
                sensor3:sensorID,
                sensor4,sensorID,
                sensor5,sensorID}

{sensorID:id, sensorName:name, temperature:temp, timeStamp:time}

Cron job will run script every 2mins
Read all sensors
Write values to sql_server on aws server

'''
import time
#import mySqlLibrary as sql
import sensor_DS18B20 as DS18B20
import peeweeModule as pw

nullTemperature = 999
w1_devices = '/sys/bus/w1/devices'

sensorLookup = {'28-0415a18d89ff':'sensor1',
                '28-0000076393f1':'sensor2',
                '28-0415a18c61ff':'sensor3',
                '28-0415a18b44ff':'sensor4',
                '28-0415a189ccff':'sensor5'}

user = 'keith.gough'
database = 'hotwater'
table = 'temperature'
#sqlCreds = sql.sqlCredentials('kg_aws_keith',database,table)

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
    
    # Confirm what devices are attached
    devIds = DS18B20.getDeviceIds()
    if debug: print(devIds)
    
    results=[]
    ts = time.strftime("%Y-%m-%d %H:%M:%S")    
    for d in devIds:
        
        # Lookup the sensor name using the id
        # If we don't find it then put a dummy entry into the dB with a suitable error
        if not d in sensorLookup:
            temp=nullTemperature
            status='Sensor {} is not in the lookup table'.format(d)
            sensorName='Sensor not named'
        else:
            temp,status = DS18B20.getTemperatureReading(d)
            sensorName = sensorLookup[d]
    
        results.append({'username':user,'sensorId':d,'temperature':temp,'statusCode':status,'sensorName':sensorName,'timestamp':ts})
    
    # Post to the AWS SQL server
    postResults(results)
    
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
