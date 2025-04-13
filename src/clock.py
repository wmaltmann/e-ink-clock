import time
from ePaperDisplay.e2in9 import EPD

print("EPD")
epd = EPD()
epd.Clear(0xff)
epd.fill(0xff)
epd.display(epd.buffer)  # Initial full update before starting partials

count = 0
while True:
    epd.fill_rect(0, 0, 128, 32, 0xff)  # Clear the area where text will go
    epd.text(str(count), 0, 0, 0x00)
    epd.display_Partial(epd.buffer)
    count += 1
    time.sleep(10)
