from lib.config import Config
from lib.datetime import DateTime
from lib.alarm_data import AlarmData
from lib.e2in9 import EPD
from lib.font import write_font
from lib.icon import write_icon
from lib.fonts.digital_80 import DIGITAL_80
from lib.fonts.sans_16 import SANS_16
from lib.icons.icons_24 import ICONS_24
from lib.icons.icons_80 import ICONS_80

TIME_CHAR_Y = 24
TIME_CHAR_X1 = 42
BATTERY_ICON_X = 268
WIFI_ICON_X = 230

class Display:
    Web_Service_On = 1
    Web_Service_Off = 0
    Web_Service_Connecting = 2

    def __init__(self, CONFIG: Config,
                 hour: int = 0,
                 minute: int = 0,
                 second: int = 0,
                 am_pm ="xx",
                 alarm_enabled: bool = False,
                 next_alarm: AlarmData | None = None,
                 voltage: float = 0.0,
                 percentage: int = 0):
        self.CONFIG = CONFIG
        self.hour = f"{hour:02}"
        self.minute = f"{minute:02}"
        self.second = f"{second:02}"
        self.am_pm = am_pm
        self.alarm_enabled = alarm_enabled
        self.next_alarm = next_alarm
        self.lower_power = False
        self.lower_power_latch = False
        self.battery_voltage = voltage
        self.battery_percentage = percentage
        self.battery_icon = "BATTERY_100"
        self.web_service_status = self.Web_Service_Off
        self.epd = EPD()
        self._initialize_display()
        self._set_battery_icon

    def update_time(self, time: DateTime):
        self.hour = f"{time.hour}"
        self.minute = f"{time.minute:02}"
        self.second = f"{time.second:02}"
        self.am_pm = time.am_pm
        self.date = time.date_string()
        self._update_display()

    def update_alarm(self, enabled: bool, next_alarm: AlarmData | None = None):
        self.alarm_enabled = enabled
        self.next_alarm = next_alarm
        self._update_display()

    def update_web_service(self, state):
        if state not in (self.Web_Service_On, self.Web_Service_Off, self.Web_Service_Connecting):
            raise ValueError("Invalid webservice state")
        self.web_service_status = state
        self._update_display()

    def update_battery(self, voltage: float, percentage: int):
        self.battery_voltage = voltage
        self.battery_percentage = percentage
        self._set_battery_icon(percentage)

    def _update_display(self):
        if self.lower_power_latch:
            return
        self._clock_mode_handler(self.CONFIG.get_clock_settings().clock_display_mode)

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

    def _mode_full_12h(self):
        self.epd.reset()
        self.epd.init()
        self.epd.fill(0xff)
        if self.lower_power:
            write_icon(self.epd, ICONS_80,"BATTERY_0", TIME_CHAR_X1, TIME_CHAR_Y, 248)
            self.lower_power_latch = True
        else:
            self._write_alarm()
            self._write_icons()
            self._write_time()
            self._write_date()
        self.epd.display(self.epd.buffer)
        self.epd.sleep()

    def _mode_partial_12h(self):
        # self.epd.reset()
        # self.epd.init()
        self.epd.fill(0xff)
        if self.lower_power:
            write_icon(self.epd, ICONS_80,"BATTERY_0", TIME_CHAR_X1, TIME_CHAR_Y, 248)
            self.lower_power_latch = True
        else:
            self._write_alarm()
            self._write_icons()
            self._write_time()
            self._write_date()
        self.epd.display_Partial(self.epd.buffer)
        # self.epd.sleep()

    def _mode_debug(self):
        self.epd.reset()
        self.epd.init()
        self.epd.fill(0xff)
        self.epd.text(f"{self.battery_voltage}", 0, 0, 0x00)
        self._write_alarm()
        self._write_icons()
        self._write_time()
        self._write_date()
        self.epd.display(self.epd.buffer)
        self.epd.sleep()

    clock_mode_handlers = {
        "full_12h": _mode_full_12h,
        "partial_12h": _mode_partial_12h,
        "debug": _mode_debug
    }

    def _clock_mode_handler(self, mode):
        handler = self.clock_mode_handlers.get(mode)
        if handler:
            handler(self)
        else:
            raise ValueError(f"Invalid clock mode: {mode}")
    
    def _write_alarm(self):
        ALARM_ICON_X = 0
        alarm_offset = 0
        if self.alarm_enabled:
            alarm_offset = write_icon(self.epd, ICONS_24,"ALARM_ON", ALARM_ICON_X, 0, 0)
        else:
            return
        alarm_text = ""
        if self.next_alarm is None:
            alarm_text = "No Alarm"
        else:
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            next_active_day = "" if self.next_alarm.next_active_day is None else days[self.next_alarm.next_active_day]
            alarm_text = f"{next_active_day} {self.next_alarm.hour_12}:{self.next_alarm.minute:02} {self.next_alarm.am_pm}"
        self.epd.text(alarm_text, alarm_offset + 4, 8, 0)
    
    def _write_icons(self):
        if self.web_service_status == self.Web_Service_Connecting:
            write_icon(self.epd, ICONS_24,"WIFI_CONFIG", WIFI_ICON_X, 0, 0)
        elif self.web_service_status == self.Web_Service_On:
            write_icon(self.epd, ICONS_24,"WIFI_ON", WIFI_ICON_X, 0, 0)
        write_icon(self.epd, ICONS_24, self.battery_icon, BATTERY_ICON_X, 0, 0)

    def _write_time(self):
        if int(self.hour) > 9 :
            write_font(self.epd, DIGITAL_80, f"!", TIME_CHAR_X1, TIME_CHAR_Y)
        time_offset = write_font(self.epd, DIGITAL_80, f"{self.hour}"[-1]+f":{self.minute}", TIME_CHAR_X1+16, TIME_CHAR_Y)
        write_font(self.epd, SANS_16, f"{self.am_pm}", time_offset, TIME_CHAR_Y + 64 , 0)

    def _write_time_old(self):
        time_offset = write_font(self.epd, DIGITAL_80, f"{self.hour}:{self.minute}", TIME_CHAR_X1, TIME_CHAR_Y ,248)
        write_font(self.epd, SANS_16, f"{self.am_pm}", time_offset, TIME_CHAR_Y + 64 , 0)

    def _write_date(self):
        self.epd.text(self.date, 106, 112, 0)