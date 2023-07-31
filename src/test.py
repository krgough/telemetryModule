'''
Created on 31 Dec 2015

@author: keith
'''

TIME_13_MS = 0x00
TIME_101_MS = 0x01
TIME_402_MS = 0x10

integrationTimeVals = {'13ms': 0x00, '101ms': 0x01, '402ms': 0x10}
gainVals = {'1x': 0x00, '16x': 0x01}


class TestClass(object):
    """Test Class"""
    def __init__(self, gain):
        self.gain = gain

    @ property
    def gain(self):
        """Get the gain setting"""
        # print("Getter")
        return self._gain

    @ gain.setter
    def gain(self, gain):
        # print('setter')
        if gain not in gainVals:
            print(
                f"ERROR: Unrecognised gain value. {gain}, "
                f"Allowed Values={gainVals.keys()}"
            )
            return
        self._gain = gain


if __name__ == "__main__":
    t = TestClass(gain='1x')
    print(t.gain)

    t.gain = '16x'
    print(t.gain)

    t.gain = '1'
    print(t.gain)
