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

class testClass(object):
    def __init__(self,xVal):
        self.y=xVal
       
    @ property
    def x(self):
        print("Getter")
        return self._x
    
    @ x.setter
    def x(self,x):
        print('setter')
        self._x=x
        
        
if __name__ == "__main__":
    t = testClass(12)
    
    print(t.x)
    t.x = 5
    print(t.x)