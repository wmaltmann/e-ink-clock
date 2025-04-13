from machine import Pin
import time

# Define the interrupt callback
def switch_changed(pin):
    if pin.value() == 0:
        print("on")
    else:
        print("off")

# Set up pin 22 as input with pull-up
switch = Pin(22, Pin.IN, Pin.PULL_UP)

# Attach interrupt on both rising and falling edges
switch.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=switch_changed)

print("Interrupt set up on GP22. Waiting for switch change...")

while True:
    time.sleep(1)