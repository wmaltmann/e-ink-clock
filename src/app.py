import time
import board
import digitalio

# Initialize the onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

print("blink2")

while True:
    led.value = True   # LED ON
    time.sleep(0.5)    # Delay for 0.5 seconds
    led.value = False  # LED OFF
    time.sleep(0.5)    # Delay for 0.5 seconds

