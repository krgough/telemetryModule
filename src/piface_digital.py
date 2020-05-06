#!/usr/bin/env python3
'''
Created on 19 Nov 2016

@author: keith
'''
import sys
import time
import pifacedigitalio  # @UnresolvedImport
# http://www.piface.org.uk/products/piface_digital_2/

NUMBER_OF_LEDS = 8

# pylint: disable=bad-continuation
PWM = {100:[1, 1, 1, 1, 0, 0, 0, 0],
        75:[1, 1, 1, 0, 0, 0, 0, 0],
        50:[1, 1, 0, 0, 0, 0, 0, 0],
        25:[1, 0, 0, 0, 0, 0, 0, 0],
         0:[0, 0, 0, 0, 0, 0, 0, 0]}
# pylint: enable=bad-continuation

def led_knight_rider(pfd):
    # pylint: disable=too-many-nested-blocks
    """
        Frame rate = 50fps
        100% = 25
         50% = 13
          0% = 0

    """
    frame_rate = 50  # 50fps = 0.02s
    led_states = [100, 75, 50, 25, 0, 0, 0, 0]
    max_frames = 500

    main_loop = True
    while main_loop:
        for _ in range(max_frames):
            # change the frame here
            for pwm_tick in range(1, 101):
                # Turn on the LEDs in the first PWM tick
                if pwm_tick == 1:
                    my_val = 0x00
                    for led in range(0, 8):
                        if led_states[led]:
                            my_val = my_val | (1 << led)    # Set a given bit

                # Turn off any expired leds
                else:
                    for led in range(0, 8):
                        if pwm_tick > led_states[led]:
                            my_val = my_val & ~(1 << led)    # Clear a given git

                pfd.output_port.value = my_val
                print(bin(my_val), time.time())
                # Sleep until next click
                time.sleep(1 / frame_rate / 100)

        return

def get_led_word(led_table, pwm_tick):
    """  LED table is a list of numbers (one for each led).  The numbers correspond to
         the number of pwmTicks that each led shall be on for.

    """
    led_word = 0xFF
    for led in range(0, 8):
        if pwm_tick > led_table[led]:
            led_word = led_word & ~(1 << led) # Clear the given bit
    return led_word
def test(pfd):
    """
        10 dimming levels is sufficient (cannot really discerne any other resolution)
        Max mark space around 50% (greater than that does not look any brighter)
        Less that 50fps shows some flicker.

        For 50fps and 20pwm ticks per frame (10 usable and 10 off) = 1/50/20 = 1ms for each pwm tick

        Testing shows that on rPi the calculations take around 300us, and the
        spi write via piface takes another 300us.

    """
    frame_count = 50
    led_table = [10, 8, 5, 3, 0, 0, 0, 0]
    max_pwm_ticks = 20
    pwm_tick = 0

    start_time = time.time()
    pfd.output_port.value = get_led_word(led_table, pwm_tick)

    for pwm_tick in range(1, (max_pwm_ticks / 2) + 1):
        pfd.output_port.value = get_led_word(led_table, pwm_tick)
        time.sleep(1 / frame_count / max_pwm_ticks)
    pfd.output_port.value = 0x00
    time.sleep(1 / frame_count / 20 / 2)  # Off for half the duty cycle
    end_time = time.time()
    print()
    print(end_time - start_time)

def single_led_test(pfd):
    """ Single LED Test
    """
    pfd.leds[7].turn_on()

    while True:
        for per in range(0, 101, 10):
            on_time = 0.01 * per / 100
            off_time = 0.02 - on_time
            print(per, on_time, off_time)
            for _ in range(500):
                pfd.leds[0].turn_on()
                time.sleep(on_time)
                pfd.leds[0].turn_off()
                time.sleep(off_time)

def main():
    """ Main Program
    """
    pfd = pifacedigitalio.PiFaceDigital() # creates a PiFace Digtal object
    test(pfd)
    sys.exit()
    #single_led_test(pfd)
    led_knight_rider(pfd)

if __name__ == "__main__":
    main()
