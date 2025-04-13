from ePaperDisplay.e2in9 import EPD

print("EPD")
epd = EPD()
epd.Clear(0xff)   
epd.fill(0xff)

epd.rect(0,0,296,128,0x00)
epd.text("XA",1,1,0x00)
epd.text("AX",288,121,0x00)
epd.display(epd.buffer)

epd.sleep()