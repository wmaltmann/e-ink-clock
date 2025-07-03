import uasyncio as asyncio
from lib.config import Config
from lib.model.datetime import Datetime
from lib.model.alarm import Alarm
from lib.model.display_context import DisplayContext
from lib.webservice import WebService
from lib.e2in9 import EPD
from lib.font import write_font
from lib.icon import write_icon
from lib.fonts.digital_80_pre import DIGITAL_80_PRE
from lib.fonts.franklin_18_pre import FRANKLIN_18_PRE
from lib.icons.icons_24 import ICONS_24
from lib.icons.icons_80 import ICONS_80

TIME_CHAR_Y = 24
TIME_CHAR_X1 = 42
BATTERY_ICON_X = 268
WIFI_ICON_X = 230
NOISE_ICON_X = 192

class Display:

    def __init__(self, CONFIG: Config, DISPLAY_CONTEXT: DisplayContext,
                 hour: int = 0,
                 minute: int = 0,
                 second: int = 0,
                 am_pm ="xx",
                 alarm_enabled: bool = False,
                 next_alarm: Alarm | None = None):
        self.CONFIG = CONFIG
        self.DISPLAY_CONTEXT = DISPLAY_CONTEXT
        self.hour = f"{hour:02}"
        self.minute = f"{minute:02}"
        self.second = f"{second:02}"
        self.am_pm = am_pm
        self.alarm_enabled = alarm_enabled
        self.next_alarm = next_alarm
        self.lower_power = False
        self.lower_power_latch = False
        self.epd = EPD()
        self.DISPLAY_CONTEXT.subscribe(self._display_updater)
    
    async def init(self):
        await self.epd.init()
        await self._initialize_display()

    async def update_time(self, time: Datetime):
        self.hour = f"{time.hour}"
        self.minute = f"{time.minute:02}"
        self.second = f"{time.second:02}"
        self.am_pm = time.am_pm
        self.date = f" {time.day_long}, {time.month_short} {time.day}"
        await self._update_display()

    async def update_alarm(self, enabled: bool, next_alarm: Alarm | None = None):
        self.alarm_enabled = enabled
        self.next_alarm = next_alarm
        await self._update_display()

    async def _update_display(self):
        if self.lower_power_latch:
            return
        await self._clock_mode_handler(self.CONFIG.get_clock_settings().clock_display_mode)

    async def _initialize_display(self):
        await self.epd.Clear(0xff)
        self.epd.fill(0xff)
        await self.epd.display(self.epd.buffer)


    async def _mode_full_12h(self):
        self.epd.reset()
        await self.epd.init()
        self.epd.fill(0xff)
        if self.lower_power:
            write_icon(self.epd, ICONS_80,"BATTERY_0", TIME_CHAR_X1, TIME_CHAR_Y, 248)
            self.lower_power_latch = True
        else:
            await self._write_alarm()
            await self._write_time()
            await self._write_date()
        await self.epd.display(self.epd.buffer)
        self.epd.sleep()

    async def _mode_partial_12h(self):
        # self.epd.reset()
        # self.epd.init()
        self.epd.fill(0xff)
        if self.lower_power:
            write_icon(self.epd, ICONS_80,"BATTERY_0", TIME_CHAR_X1, TIME_CHAR_Y, 248)
            self.lower_power_latch = True
        else:
            await asyncio.sleep_ms(0)
            await self._write_alarm()
            await asyncio.sleep_ms(0)
            await asyncio.sleep_ms(0)
            await self._write_time()
            await asyncio.sleep_ms(0)
            await self._write_date()
            await asyncio.sleep_ms(0)
        
        await asyncio.sleep_ms(0)
        await self.epd.display_Partial(self.epd.buffer)
        # self.epd.sleep()

    async def _mode_debug(self):
        self.epd.reset()
        await self.epd.init()
        self.epd.fill(0xff)
        self.epd.text(f"{self.DISPLAY_CONTEXT.battery_voltage}", 0, 0, 0x00)
        await self._write_alarm()
        await self._write_time()
        await self._write_date()
        await self.epd.display(self.epd.buffer)
        self.epd.sleep()

    clock_mode_handlers = {
        "full_12h": _mode_full_12h,
        "partial_12h": _mode_partial_12h,
        "debug": _mode_debug
    }

    async def _clock_mode_handler(self, mode):
        handler = self.clock_mode_handlers.get(mode)
        if handler:
            await handler(self)
        else:
            raise ValueError(f"Invalid clock mode: {mode}")
    
    async def _write_alarm(self):
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

    async def _write_time(self):
        if int(self.hour) > 9 :
            await write_font(self.epd, DIGITAL_80_PRE, f"!", TIME_CHAR_X1, TIME_CHAR_Y)
        time_offset = await write_font(self.epd, DIGITAL_80_PRE, f"{self.hour}"[-1]+f":{self.minute}", TIME_CHAR_X1+16, TIME_CHAR_Y)

        await write_font(self.epd, FRANKLIN_18_PRE, f"{self.am_pm}", time_offset + 4, TIME_CHAR_Y + 64 , 24)
    
    async def _write_date(self):
            await write_font(self.epd, FRANKLIN_18_PRE, f"{self.date}", 0, 110, 296)

#----------------- Asynchronous Drawing Methods -----------------

    def _display_updater(self, changes : set[str]):
        print(f"Display update requested with changes: {changes}")
        if "battery_icon" in changes:
            asyncio.create_task(self._draw_battery_icon())
        if "noise_player_mode" in changes:
            asyncio.create_task(self._draw_noise_icon())
        if "web_service_status" in changes:
            asyncio.create_task(self._draw_web_service_icon())

    async def _draw_battery_icon(self):
        await asyncio.sleep_ms(0)
        write_icon(self.epd, ICONS_24, self.DISPLAY_CONTEXT.battery_icon, BATTERY_ICON_X, 0, 0)
        await asyncio.sleep_ms(0)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_noise_icon(self):
        await asyncio.sleep_ms(0)
        if self.DISPLAY_CONTEXT.noise_player_mode == "Brown":
            write_icon(self.epd, ICONS_24, "WAVE", NOISE_ICON_X, 0, 0)
        else:
            self.epd.fill_rect(NOISE_ICON_X, 0, 24, 24, 0xff)
        await asyncio.sleep_ms(0)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_web_service_icon(self):
        await asyncio.sleep_ms(0)
        if self.DISPLAY_CONTEXT.web_service_status == WebService.WEB_SERVICE_CONNECTING:
            write_icon(self.epd, ICONS_24, "WIFI_CONFIG", WIFI_ICON_X, 0, 0)
        elif self.DISPLAY_CONTEXT.web_service_status == WebService.WEB_SERVICE_ON:
            write_icon(self.epd, ICONS_24, "WIFI_ON", WIFI_ICON_X, 0, 0)
        else:
            self.epd.fill_rect(WIFI_ICON_X, 0, 24, 24, 0xff)
        await asyncio.sleep_ms(0)
        await self.epd.display_Partial(self.epd.buffer)