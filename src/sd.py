import machine
import os
from utils.sdcard import SDCard 
import uos

# Initialize SPI0 (SPI ID 0: SCK=GP18, MOSI=GP19, MISO=GP16)
spi = machine.SPI(0, baudrate=1_000_000, polarity=0, phase=0,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))

# Chip Select pin
cs = machine.Pin(17, machine.Pin.OUT)

# Initialize SD card
sd = SDCard(spi, cs)

# Mount SD card
vfs = uos.VfsFat(sd) # type: ignore
uos.mount(vfs, "/sd")

# Test file write
with open("/sd/hello.txt", "w") as f:
    f.write("Hello from Pico!")

# List SD contents
print("Files on SD card:", os.listdir("/sd"))
