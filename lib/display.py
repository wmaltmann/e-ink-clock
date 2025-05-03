from lib.datetime import DateTime
from lib.e2in9 import EPD
from lib.font import write_font
from lib.icon import write_icon
from lib.fonts.digital_80 import DIGITAL_80
from lib.fonts.sans_16 import SANS_16
from lib.icons.icons_24 import ICONS_24
from lib.icons.icons_80 import ICONS_80

TIME_CHAR_Y = 24
TIME_CHAR_X1 = 24
ALARM_ICON_X = 0
BATTERY_ICON_X = 268

class Display:
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, am_pm ="xx", alarm_enabled: bool = False, voltage: float = 0.0, percentage: int = 0):
        self.hour = f"{hour:02}"
        self.minute = f"{minute:02}"
        self.second = f"{second:02}"
        self.am_pm = am_pm
        self.alarm_enabled = alarm_enabled
        self.lower_power = False
        self.lower_power_latch = False
        self.battery_voltage = voltage
        self.battery_percentage = percentage
        self.battery_icon = "BATTERY_100"
        self.epd = EPD()
        self._initialize_display()
        self._set_battery_icon

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
        self._set_battery_icon(percentage)

    def _update_display(self):
        if self.lower_power_latch:
            return
        self.epd.reset()
        self.epd.init()
        self.epd.fill(0xff)
        if self.lower_power:
            write_icon(self.epd, ICONS_80,"BATTERY_0", TIME_CHAR_X1, TIME_CHAR_Y, 248)
            self.lower_power_latch = True
        else:
            if self.alarm_enabled:
                write_icon(self.epd, ICONS_24,"ALARM_ON", ALARM_ICON_X, 0, 0)
            write_icon(self.epd, ICONS_24, self.battery_icon, BATTERY_ICON_X, 0, 0)
            time_offset = write_font(self.epd, DIGITAL_80, f"{self.hour}:{self.minute}", TIME_CHAR_X1, TIME_CHAR_Y ,248)
            write_font(self.epd, SANS_16, f"{self.am_pm}", time_offset, TIME_CHAR_Y + 64 , 0)
        self.epd.display(self.epd.buffer)
        self.epd.sleep()

    def _initialize_display(self):
        self.epd.Clear(0xff)
        self.epd.fill(0xff)
        self.epd.display(self.epd.buffer)

    def _set_battery_icon(self, percentage: int):
        if percentage == 0 :
            self.battery_icon = "BATTERY_0"
            self.lower_power = True
        elif percentage <= 20:
            self.battery_icon = "BATTERY_0"
            self.lower_power = False
            self.lower_power_latch = False
        elif percentage <= 50:
            self.battery_icon = "BATTERY_25"
            self.lower_power = False
            self.lower_power_latch = False
        elif percentage <= 60:
            self.battery_icon = "BATTERY_50"
            self.lower_power = False
            self.lower_power_latch = False
        elif percentage <= 80:
            self.battery_icon = "BATTERY_75"
            self.lower_power = False
            self.lower_power_latch = False
        else:
            self.battery_icon = "BATTERY_100"
            self.lower_power_latch = False