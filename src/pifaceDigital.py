'''
Created on 19 Nov 2016

@author: keith
'''
import time
import pifacedigitalio
# http://www.piface.org.uk/products/piface_digital_2/

NUMBER_OF_LEDS=8

PWM = {100:[1,1,1,1,0,0,0,0],
        75:[1,1,1,0,0,0,0,0],
        50:[1,1,0,0,0,0,0,0],
        25:[1,0,0,0,0,0,0,0],
         0:[0,0,0,0,0,0,0,0]}

def ledKnightRider(pfd):
    """
        Frame rate = 50fps
        100% = 25
         50% = 13
          0% = 0

    """
    frameRate=50         # 50fps = 0.02s
    ledStates=[100,75,50,25,0,0,0,0]
    maxFrames=500

    mainLoop=True
    while mainLoop:
        for frameCount in range(maxFrames):
            # change the frame here
            for pwmTick in range(1,101):
                # Turn on the LEDs in the first PWM tick
                if pwmTick==1:
                    myVal=0x00
                    for led in range(0,8):
                        if ledStates[led]:
                            myVal = myVal | (1 << led)    # Set a given bit

                # Turn off any expired leds
                else:
                    for led in range(0,8):
                        if pwmTick > ledStates[led]:
                            myVal = myVal & ~(1 << led)    # Clear a given git

                pfd.output_port.value=myVal
                print(bin(myVal),time.time())
                # Sleep until next click
                time.sleep(1/frameRate/100)

        return

def getLedWord(ledTable, pwmTick):
    """  LED table is a list of numbers (one for each led).  The numbers correspond to
         the number of pwmTicks that each led shall be on for.

    """
    ledWord=0xFF
    for led in range(0,8):
        if pwmTick > ledTable[led]:
            ledWord = ledWord & ~(1 << led) # Clear the given bit
    return ledWord
def test(pfd):
    """
        10 dimming levels is sufficient (cannot really discerne any other resolution)
        Max mark space around 50% (greater than that does not look any brighter)
        Less that 50fps shows some flicker.

        For 50fps and 20pwm ticks per frame (10 usable and 10 off) = 1/50/20 = 1ms for each pwm tick

        Testing shows that on rPi the calculations take around 300us, and the
        spi write via piface takes another 300us.

    """
    frameCount=50
    ledTable=[10,8,5,3,0,0,0,0]
    maxPwmTicks=20
    pwmTick=0

    startTime=time.time()
    pfd.output_port.value=getLedWord(ledTable, pwmTick)

    for pwmTick in range(1,(maxPwmTicks/2)+1):
        pfd.output_port.value=getLedWord(ledTable, pwmTick)
        time.sleep(1/frameCount/maxPwmTicks)
    pfd.output_port.value=0x00
    time.sleep(1/frameCount/20/2)  # Off for half the duty cycle
    endTime=time.time()
    print()
    print(endTime-startTime)

def singleLedTest(pfd):
    """ Single LED Test
    """
    pfd.leds[7].turn_on()
    onPercent=100

    while True:
        for per in range(0,101,10):
            onTime=0.01*per/100
            offTime=0.02-onTime
            print(per,onTime,offTime)
            for i in range(500):
                pfd.leds[0].turn_on()
                time.sleep(onTime)
                pfd.leds[0].turn_off()
                time.sleep(offTime)

def main():
    """ Main Program
    """
    pfd = pifacedigitalio.PiFaceDigital() # creates a PiFace Digtal object
    test(pfd)
    exit()
    #singleLedTest(pfd)
    ledKnightRider(pfd)

if __name__=="__main__":
    main()
