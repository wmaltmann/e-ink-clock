from machine import Pin
import time

# Define the interrupt callback
def switch_changed():
    print(f"Interrupt triggered on 15")

def switch_changed2():
    print(f"Interrupt triggered on 6")

def switch_changed3():
    print(f"Interrupt triggered on 7")

def switch_changed4():
    print(f"Interrupt triggered on 14")


# Set up pins as input with pull-up
switch_15 = Pin(15, Pin.IN, Pin.PULL_UP)
switch_6 = Pin(6, Pin.IN, Pin.PULL_UP)
switch_7 = Pin(7, Pin.IN, Pin.PULL_UP)
switch_14 = Pin(14, Pin.IN, Pin.PULL_UP)

# Attach interrupts on falling edges
switch_15.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: switch_changed())
switch_6.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: switch_changed2())
switch_7.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: switch_changed3())
switch_14.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: switch_changed4())

print("Interrupts set up on GP15, GP6, GP7, and GP14. Waiting for switch changes...")

while True:
    time.sleep(1)