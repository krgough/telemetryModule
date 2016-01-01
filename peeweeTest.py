'''
Created on 31 Dec 2015

@author: keith
'''


import peewee as pw
import mySQL_Library as sql_Lib

sqlCreds = sql_Lib.sqlCredentials('kg_aws_keith','isopBeta','devices')

db = pw.MySQLDatabase('isopBeta',user=sqlCreds.username,host=sqlCreds.host,password=sqlCreds.password)

class mySQLModel(pw.Model):
    """ A base model for mySQL database """
    class Meta:
        database = db
        
class devices(mySQLModel):
    """
    """
    username = pw.CharField()
    deviceID = pw.CharField(primary_key=True)
    deviceType = pw.CharField()
    present = pw.BooleanField()
    firmware = pw.CharField()
    lastUpdate = pw.TimeField()

db.connect()

for d in devices.select():
    print(d.username,d.deviceID)

print()
user = devices.select().where((devices.username=='muhammad_s_patel@hotmail.com') & (devices.deviceType=='HAHVACThermostat'))

for u in user:
    print(u.username,u.deviceType)


db.close()
print('All Done')