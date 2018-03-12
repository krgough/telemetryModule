'''
Created on 1 Jul 2016

@author: keith

Measure the LUX output for a given illumination levels.
Soak for some extended period
Results printed to console so redirect to file is advisable

'''
import threadedSerial as AT
import readLightLevels as rll

from os import path
from getopt import getopt
import sys,glob

""" Command line argument methods """
def readArguments():
    """ Read command line parameters 
        Use them if provided.
    """
    helpString = "\nUSAGE: {} [-h] -n nodeId -e endpoint -p port -b baud\n\n".format(path.basename(sys.argv[0])) +\
                 "Use these command line options to select the node, endpoint, uart port and baud\n\n" +\
                 "-h             Print this help\n" +\
                 "-n node        Node ID of target node\n" +\
                 "-e endpoint    Endpoint of the target node\n" +\
                 "-p port        /dev/portId\n" +\
                 "-b baud        usually 115200\n"

    myNodeId = None
    myEp = None
    myPort = None
    myBaud = None

    opts = getopt(sys.argv[1:], "hn:e:p:b:")[0]
    
    for opt, arg in opts:
        #print(opt, arg)
        if opt == '-h':
            print(helpString)
            exit()
        if opt == '-n':
            myNodeId = arg.upper()
        if opt == '-e':
            myEp = arg
        if opt == '-p':
            myPort = arg
        if opt == '-b':
            myBaud = arg

    
    if not myNodeId:
        print("Node ID was not specified")
        print(helpString)
        exit()
        
    if not myEp:
        print("EP ID was not specified")
        print(helpString)
        exit()
        
    if not myPort:
        print("UART port was not specified.  Try one of these...")
        print(glob.glob("/dev/tty.*"))
        print(helpString)
        exit()
        
    if not myBaud:
        print("Baud rate not specified.  Typically we use 115200")
        print(helpString)
        exit()
        
    return myNodeId, myEp, myPort, myBaud

def setLevel(nodeId,epId,level):
    """
    """
    level = "{:02x}".format(int(level/100*254))
    
    respState, respCode, respValue=AT.moveToLevel(nodeId,epId,myLevel=level)
    if not respState:
        print("ERROR: moveToLevel has failed. {}".format(respCode,respValue))
        exit()
    return
def main():
    nodeId, ep, port, baud = readArguments()
    AT.startSerialThreads(port,baud,printStatus=False,rxQ=True,listenerQ=False)
    
    level = 70 # Light level as percentage
    setLevel(nodeId,ep,level)
        
    # Now read and print the levels for 1 min
    rll.TAG="{}%".format(level)
    rll.params['duration'] = 60*60*2  # 2 hours
    rll.params['period'] = 1          # 1 second
    rll.main(rll.params)
    
    return
    
if __name__== "__main__":
    main()
    print('All done.')