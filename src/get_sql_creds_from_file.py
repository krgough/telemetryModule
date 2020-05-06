#! /user/bin/env python3
'''
Created on 5 Jan 2016

@author: keith
'''
import logging
LOGGER = logging.getLogger(__name__)

SQL_CREDENTIAL_FILE = ('/Users/Keith.Gough/Dropbox/repositories/Python/'
                      'alertme_api_logs/cfg/mysqlCreds.txt')

class SqlCredentials:
    """ Load the wanted credentials from the sql credential file
    """
    def __init__(self, credential_file, credential_id):
        self.cred_dict = {}
        with open(credential_file, mode='r') as file:
            for line in file:
                line_text = line.strip().split(',')
                if not line_text[0] in self.cred_dict:
                    self.cred_dict[line_text[0]] = {}
                self.cred_dict[line_text[0]][line_text[1]] = line_text[2]

        if credential_id in self.cred_dict:
            self.username = self.cred_dict[credential_id]['username']
            self.password = self.cred_dict[credential_id]['password']
            self.host = self.cred_dict[credential_id]['host']
        else:
            self.username = None
            self.password = None
            self.host = None

    def print_all(self):
        """ Print a list of all the databases in the credential file
        """
        for database in self.cred_dict:
            print(database)

    def __repr__(self):
        """ Return a list of strings
        """
        my_string = ["Username = {}".format(self.username),
                     'Password = {}'.format(self.password),
                     'Host     = {}'.format(self.host),
                    ]
        return "\n".join(my_string)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    CREDS = SqlCredentials(SQL_CREDENTIAL_FILE, 'fred')
    CREDS.print_all()
