'''
Created on 31 Dec 2015

@author: keith
'''
#TODO: Create a database and table on the aws sql server
#TODO: 

"""

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

"""
import os,sys,time
import mySQL_Library as sql

nullTemperature = 999
w1_devices = '/sys/bus/w1/devices'

sensorLookup = {'28-0415a189ccff':'sensor1',
                '28-0415a18d89ff':'sensor2',
                '':'sensor3',
                '':'sensor4',
                '':'sensor5'}

user = 'keith.gough'
database = 'hotwater'
table = 'temperature'
sqlCreds = sql.sqlCredentials('kg_aws_keith',database,table)

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
def postResults(results):
    """ Insert the results into the mySQL database on the server
    
    """
    for r in results:
        resp = sql.insertNewEntry(sqlCreds, table, r)
        print(resp)
    return

if __name__ == "__main__":
    debug = False
    
    devIds = getDeviceIds()
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
            temp,status = getTemperatureReading(d)
            sensorName = sensorLookup[d]
    
        results.append({'user':user,'sensorId':d,'temperature':temp,'statusCode':status,'sensorName':sensorName,'timestamp':ts})
    
    for r in results:
        print(r)
    
    postResults(results)
    #print("{},{:10.2f}'C,{}".format(d,temp,status))
