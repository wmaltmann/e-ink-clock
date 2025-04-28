from lib.datetime import DateTime
from lib.e2in9 import EPD
from lib.font import write_font
from lib.fonts.digital_80 import DIGITAL_80
from lib.fonts.sans_16 import SANS_16

TIME_CHAR_Y = 24
TIME_CHAR_X1 = 24
TIME_CHAR_X2 = 84
TIME_CHAR_X3 = 144
TIME_CHAR_X4 = 152
TIME_CHAR_X5 = 212
TIME_CHAR_X6 = 272

class Display:
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, am_pm ="xx", alarm_enabled: bool = False, voltage: float = 0.0, percentage: int = 0):
        self.hour = f"{hour:02}"
        self.minute = f"{minute:02}"
        self.second = f"{second:02}"
        self.am_pm = am_pm
        self.alarm_enabled = alarm_enabled
        self.battery_voltage = voltage
        self.battery_percentage = percentage
        self.epd = EPD()
        self._initialize_display()

    def update_time(self, time: DateTime):
        self.hour = f"{time.hour}"
        self.minute = f"{time.minute:02}"
        self.second = f"{time.second:02}"
        self.am_pm = time.am_pm
        self._update_display()

    def update_alarm(self, enabled: bool):
        self.alarm_enabled = enabled
        self._update_display()

    def update_battery(self, voltage: float, percentage: int):
        self.battery_voltage = voltage
        self.battery_percentage = percentage

    def _update_display(self):
        self.epd.reset()
        self.epd.init()
        self.epd.fill(0xff)
        if self.alarm_enabled:
            self.epd.fill_rect(0, 0, 24, 24, 0x00)
        self.epd.text(f"{self.battery_voltage}", 200, 2, 0x00)
        x_offest = write_font(self.epd, DIGITAL_80, f"{self.hour}:{self.minute}", TIME_CHAR_X1, TIME_CHAR_Y ,248)
        write_font(self.epd, SANS_16, f"{self.am_pm}", x_offest, TIME_CHAR_Y + 64 , 0)
        self.epd.display(self.epd.buffer)
        self.epd.sleep()

    def _initialize_display(self):
        self.epd.Clear(0xff)
        self.epd.fill(0xff)
        self.epd.display(self.epd.buffer)