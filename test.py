'''
Created on 31 Dec 2015

@author: keith
'''
import time

def myError(returnError):
    """
    """
    if not returnError:
        return 0
    else:
        return "error string"
    
    
resp = myError(returnError=True)

if resp:
    print('ERROR {}'.format(resp))