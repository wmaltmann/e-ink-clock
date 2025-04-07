from ePaperDisplay.e2in9 import EPD
from ePaperDisplay.fonts import freesans20
from ePaperDisplay.writer import Writer
import framebuf

class FrameBufferWithWH(framebuf.FrameBuffer):
    def __init__(self, buf, width, height, format):
        super().__init__(buf, width, height, format)
        self.width = width
        self.height = height


epd = EPD()
epd.Clear(0xff)

epd.fill(0xff)
epd.text("Waveshare", 5, 10, 0x00)
epd.text("Pico_ePaper-2.9", 5, 20, 0x00)
epd.text("Raspberry Pico", 5, 30, 0x00)
epd.display_Partial(epd.buffer)
epd.delay_ms(2000)
