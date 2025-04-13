import sys
sys.path.append("/src")

import clock  # this runs clock.py


import machine

# Initialize the LED pin
led = machine.Pin(25, machine.Pin.OUT)
led.value(1)
