'''
Created on 31 Dec 2015

@author: keith
'''

import time
import peewee as pw  # @UnresolvedImport
import get_sql_creds_from_file as sql_creds

SQL_CRED_ID = 'kg_aws_keith'
DATABASE = 'hotwater'

SQL_CREDENTIAL_FILE = sql_creds.SQL_CREDENTIAL_FILE
SQL_CREDS = sql_creds.SqlCredentials(SQL_CREDENTIAL_FILE, SQL_CRED_ID)

DB_HOTWATER = pw.MySQLDatabase(DATABASE,
                               USER=SQL_CREDS.username,
                               host=SQL_CREDS.host,
                               password=SQL_CREDS.password)

class Hotwater(pw.Model):
    """ A base model for mySQL DATABASE """
    class Meta:
        DATABASE = DB_HOTWATER

# Model for hotwater.temperature TABLE
class Temperature(Hotwater):
    """ This class describes the columns in the 'temperature' TABLE in the DATABASE
    """
    id = pw.IntegerField(primary_key=True)
    username = pw.CharField()
    sensorName = pw.CharField()
    sensorId = pw.CharField()
    temperature = pw.IntegerField()
    statusCode = pw.CharField()
    timestamp = pw.DateTimeField()

def insert_rows(dbase, table, data):
    """ Will insert rows atomically in the fastest way.
        data = [{},{}] where each dict should contain the column names and wanted values.
    """
    error_state = False
    resp = None
    #try:
    with dbase.atomic():
        table.insert_many(data).execute()
    #except Exception as e:
    #    resp="ERROR: {}".format(e)
    return resp, error_state

def select_where(table, *expressions):
    """ Select Where...
    """
    error_state = False
    resp = None
    try:
        resp = table.select().where(expressions)
    except Exception as err:
        resp = "ERROR: {}".format(err)
        print(resp)
    return resp, error_state
def select_all(table):
    """ Select All
    """
    error_state = False
    resp = None
    try:
        resp = table.select()
    except (pw.PeeweeException, pw.OperationalError) as err:
        resp = "ERROR: {}".format(err)
        print(resp)
    return resp, error_state

def test_insert_junk_row(dbase, table):
    """ Insert a row
    """
    data = [{'username':'junk1',
             'sensorName':'junkSensor',
             'sensorId':'ABC_JUNK',
             'temperature':12345,
             'statusCode':'This_is_junk',
             'timestamp':time.strftime("%Y-%m-%d %H:%M:%S")}]
    resp, err_status = insert_rows(dbase, table, data)
    if err_status:
        print(resp)
    else:
        print("Row inserted")

def test_get_rows(dbase, table):
    """ Get rows
    """
    resp, err_status = select_where(dbase,
                                    table,
                                    (table.sensorName == 'sensor1' &
                                     table.timestamp > '2016-01-05 00:00'))
    if not err_status:
        for dat in resp:
            print(dat.sensorName, dat.timestamp, dat.temperature)
    else:
        print(resp)

if __name__ == "__main__":

    # Tests - Insert dummy data
    test_insert_junk_row(DB_HOTWATER, table = "temperature")
    test_get_rows(DB_HOTWATER, table = "temperature")
    print('All Done')
