'''
Created on 31 Dec 2015

@author: keith
'''

import peewee as pw
import filePaths as fp
import time

sqlCredId = 'kg_aws_keith'
database = 'hotwater'

sqlCredentialFile = fp.sqlCredentialFile
sqlCreds = fp.sqlCredentials(sqlCredId)

db_Hotwater = pw.MySQLDatabase(database,user=sqlCreds.username,host=sqlCreds.host,password=sqlCreds.password)

class hotwater(pw.Model):
    """ A base model for mySQL database """
    class Meta:
        database = db_Hotwater

# Model for hotwater.temperature table      
class temperature(hotwater):
    """ This class describes the columns in the 'temperature' table in the database
    """
    id = pw.IntegerField(primary_key=True)
    username = pw.CharField()
    sensorName = pw.CharField()
    sensorId = pw.CharField()
    temperature = pw.IntegerField()
    statusCode = pw.CharField()
    timestamp = pw.DateTimeField()

def insertRows(db,table,data):
    """ Will insert rows atomically in the fastest way.
        data = [{},{}] where each dict should contain the column names and wanted values.
    """
    errorState = False
    resp = None
    #try:
    with db.atomic():
        table.insert_many(data).execute()
    #except Exception as e:
    #    resp="ERROR: {}".format(e)
    return resp,errorState 
def selectWhere(db,table,*expressions):
    """
    """
    errorState = False
    resp = None
    try:
        resp = table.select().where(expressions)
    except Exception as e:
        resp = "ERROR: {}".format(e)
        print(resp)
    return resp,errorState
def selectAll(db,table):
    """
    """
    errorState = False
    resp = None
    try:
        resp = table.select()
    except (pw.PeeweeException,pw.OperationalError) as e:
        resp = "ERROR: {}".format(e)
        print(resp)
    return resp,errorState

def test_InsertJunkRow(db,table):
    """
    """
    data = [{'username':'junk1',
             'sensorName':'junkSensor',
             'sensorId':'ABC_JUNK',
             'temperature':12345,
             'statusCode':'This_is_junk',
             'timestamp':time.strftime("%Y-%m-%d %H:%M:%S")}]
    resp,errStatus=insertRows(db, table, data)
    print(resp) if errStatus else print("Row inserted") 
    return
def test_getRows(db):
    """
    """
    resp,errStatus = selectWhere(db, temperature, (temperature.sensorName=='sensor1') & (temperature.timestamp>'2016-01-05 00:00'))
    if not errStatus:
        for r in resp:
            print(r.sensorName,r.timestamp,r.temperature)
    else:
        print(resp)
    return

if __name__ == "__main__":
    
    """ Tests """
        
    # Insert dummy data
    test_InsertJunkRow(db_Hotwater,temperature)
    test_getRows(db_Hotwater)

    print('All Done')