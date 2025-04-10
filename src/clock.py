from ePaperDisplay.e2in9 import EPD

print("EPD")
epd = EPD()
epd.Clear(0xff)   
epd.fill(0xff)

for i in range(0, 10):
    epd.fill_rect(0, 0, 10, 10, 0xff)
    epd.text(str(i), 0, 0, 0x00)
    epd.display_Partial(epd.buffer)

epd.sleep()