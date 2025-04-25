from lib.datetime import DateTime
from lib.e2in9 import EPD

class Display:
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, am_pm ="xx"):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.am_pm = am_pm
        self.epd = EPD()
        self._initialize_display()

    def update_time(self, time: DateTime):
        self.hour = time.hour
        self.minute = time.minute
        self.second = time.second
        self.am_pm = time.am_pm
        self._update_display()

    def _update_display(self):
        self.epd.reset()
        self.epd.init()
        self._initialize_display()
        time_sting = f"{self.hour:02d}:{self.minute:02d} {self.am_pm}"
        self.epd.fill_rect(20,60,256,8, 0Xff)
        self.epd.text(time_sting, 100, 60, 0x00)
        self.epd.display_Partial()
        self.epd.sleep()

    def _initialize_display(self):
        self.epd.Clear(0xff)
        self.epd.fill(0xff)
        self.epd.display(self.epd.buffer)

    def line(self):
        self.epd.reset()
        self.epd.init()
        self._initialize_display()
        self.epd.fill_rect(0,0,10,10, 0x00)
        self.epd.display_Partial()
        self.epd.sleep()