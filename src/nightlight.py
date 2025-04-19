from machine import Pin, PWM
from time import sleep

# Configure GP5 as a PWM output pin
led = PWM(Pin(5))
led.freq(1000)  # Set frequency to 1 kHz

# Set the desired percentage (0 to 100)
percent = 5  # Change this value to set the duty cycle percentage

# Convert percentage to duty cycle value (0 to 65535)
duty_cycle = int((percent / 100) * 65535)

while True:
    led.duty_u16(duty_cycle)  # Set duty cycle to the desired percentage
    sleep(1)  # Wait for 1 second
    led.duty_u16(0)  # Set duty cycle to 0
    sleep(1)  # Wait for 1 second
