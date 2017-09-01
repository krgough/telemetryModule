'''
Created on 5 Jan 2016

@author: keith
'''
sqlCredentialFile='/Users/keith/Google Drive/Python/alertme_api_logs/cfg/mysqlCreds.txt'

class sqlCredentials(object):
    """ Load the wanted credentials from the sql credential file
    """
    def __init__(self,credentialId,database=None,table=None):
        credDict = {}
        with open(sqlCredentialFile, mode='r') as f:
            for line in f:
                lineText = line.strip().split(',')
                if not lineText[0] in credDict:
                    credDict[lineText[0]]={}
                credDict[lineText[0]][lineText[1]]=lineText[2]
                
        self.username = credDict[credentialId]['username']
        self.password = credDict[credentialId]['password']
        self.host = credDict[credentialId]['host']
        self.database = database
        self.table = table