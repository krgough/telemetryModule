'''
Created on 31 Dec 2015

@author: keith
'''
import time

time_13ms  = 0x00
time_101ms = 0x01
time_402ms = 0x10

integrationTimeVals = {'13ms':0x00,'101ms':0x01,'402ms':0x10}
gainVals = {'1x':0x00,'16x':0x01}

class testClass(object):
    def __init__(self,gain):
        self.gain=gain
       
    @ property
    def gain(self):
        #print("Getter")
        return self._gain
    
    @ gain.setter
    def gain(self,gain):
        #print('setter')
        if not gain in gainVals:
            print("ERROR: Unrecognised gain value. {}, Allowed Values={}".format(gain,list(gainVals.keys())))
            return
        self._gain=gain
        
if __name__ == "__main__":
    t = testClass(gain='1x')
    print(t.gain)
    
    t.gain = '16x'
    print(t.gain)
    
    t.gain = '1'
    print(t.gain)