from machine import Pin, PWM
import time

# Configure GPIO 21 as a PWM output
vibration_pin = 21
frequency = 1000  # Frequency in Hz

# Initialize PWM on GPIO 21
pwm = PWM(Pin(vibration_pin))
pwm.freq(frequency)

def vibrate(duty_cycle_percent):
    """
    Vibrates the motor with a specified duty cycle percentage.
    
    :param duty_cycle_percent: Duty cycle percentage (0-100)
    """
    duty_cycle_u16 = int((duty_cycle_percent / 100) * 65535)
    pwm.duty_u16(duty_cycle_u16)

# Main loop: Vibrate for 1 second, then off for 1 second
while True:
    vibrate(100)  # 50% duty cycle
    time.sleep(1)  # Vibrate for 1 second
    vibrate(0)  # Turn off the motor
    time.sleep(1)  # Off for 1 second