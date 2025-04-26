from lib.datetime import DateTime
from lib.e2in9 import EPD
from lib.time_font import write_time_font

TIME_CHAR_Y = 24
TIME_CHAR_X1 = 24
TIME_CHAR_X2 = 84
TIME_CHAR_X3 = 144
TIME_CHAR_X4 = 152
TIME_CHAR_X5 = 212
TIME_CHAR_X6 = 272

class Display:
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, am_pm ="xx"):
        self.hour = f"{hour:02}"
        self.minute = f"{minute:02}"
        self.second = f"{second:02}"
        self.am_pm = am_pm
        self.epd = EPD()
        self._initialize_display()

    def update_time(self, time: DateTime):
        self.hour = f"{time.hour:02}"
        self.minute = f"{time.minute:02}"
        self.second = f"{time.second:02}"
        self.am_pm = time.am_pm
        self._update_display()

    def _update_display(self):
        self.epd.reset()
        self.epd.init()
        self._initialize_display()
        if self.hour[0] != '0':
            write_time_font(self.epd, str(self.hour)[0], TIME_CHAR_X1, TIME_CHAR_Y )
        write_time_font(self.epd, str(self.hour)[1], TIME_CHAR_X2, TIME_CHAR_Y )
        write_time_font(self.epd, ":", TIME_CHAR_X3, TIME_CHAR_Y )
        write_time_font(self.epd, str(self.minute)[0], TIME_CHAR_X4, TIME_CHAR_Y )
        write_time_font(self.epd, str(self.minute)[1], TIME_CHAR_X5, TIME_CHAR_Y )
        if self.am_pm == "AM" or self.am_pm == "PM":
            write_time_font(self.epd, self.am_pm, TIME_CHAR_X6, TIME_CHAR_Y )
        self.epd.display_Partial()
        self.epd.sleep()

    def _initialize_display(self):
        self.epd.Clear(0xff)
        self.epd.fill(0xff)
        self.epd.display(self.epd.buffer)