from machine import Pin
import time

# Set GPIO pin 21 as output
vibration_motor = Pin(21, Pin.OUT)

# Function to activate the motor
def vibrate(duration_ms):
    vibration_motor.high()  # Turn on the motor
    time.sleep_ms(duration_ms)  # Wait for the specified duration
    vibration_motor.low()  # Turn off the motor

# Example usage: Vibrate for 500 milliseconds
vibrate(10000)