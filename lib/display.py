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
TIME_CHAR_X2 = TIME_CHAR_X1 + 16
TIME_CHAR_X3 = TIME_CHAR_X2 + 60
TIME_CHAR_X4 = TIME_CHAR_X3 + 16
TIME_CHAR_X5 = TIME_CHAR_X4 + 60
TIME_CHAR_X6 = TIME_CHAR_X5 + 62
BATTERY_ICON_X = 268
WIFI_ICON_X = 230
NOISE_ICON_X = 192

class Display:

    def __init__(self, CONFIG: Config, DISPLAY_CONTEXT: DisplayContext):
        self.CONFIG = CONFIG
        self.DISPLAY_CONTEXT = DISPLAY_CONTEXT
        self.initialized = False
        self.epd = EPD()
        self.DISPLAY_CONTEXT.subscribe(self._display_updater)
    
    async def init(self):
        await self.epd.init()
        self.epd.reset()
        await self.epd.Clear(0xff)
        self.epd.fill(0xff)
        await self.epd.display(self.epd.buffer)
        await self._draw_time_div()
        self.initialized = True
    
    # async def _write_alarm(self):
    #     ALARM_ICON_X = 0
    #     alarm_offset = 0
    #     if self.alarm_enabled:
    #         alarm_offset = write_icon(self.epd, ICONS_24,"ALARM_ON", ALARM_ICON_X, 0, 0)
    #     else:
    #         return
    #     alarm_text = ""
    #     if self.next_alarm is None:
    #         alarm_text = "No Alarm"
    #     else:
    #         days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    #         next_active_day = "" if self.next_alarm.next_active_day is None else days[self.next_alarm.next_active_day]
    #         alarm_text = f"{next_active_day} {self.next_alarm.hour_12}:{self.next_alarm.minute:02} {self.next_alarm.am_pm}"
    #     self.epd.text(alarm_text, alarm_offset + 4, 8, 0)     

    # async def _write_time(self):
    #     if int(self.hour) > 9 :
    #         await write_font(self.epd, DIGITAL_80_PRE, f"!", TIME_CHAR_X1, TIME_CHAR_Y)
    #     time_offset = await write_font(self.epd, DIGITAL_80_PRE, f"{self.hour}"[-1]+f":{self.minute}", TIME_CHAR_X1+16, TIME_CHAR_Y)

    #     await write_font(self.epd, FRANKLIN_18_PRE, f"{self.am_pm}", time_offset + 4, TIME_CHAR_Y + 64 , 24)
    
    # async def _write_date(self):
    #         await write_font(self.epd, FRANKLIN_18_PRE, f"", 0, 110, 296)

#----------------- Asynchronous Drawing Methods -----------------

    def _display_updater(self, changes : set[str]):
        if not self.initialized:
            print("Display not initialized, skipping update.")
            return
        print(f"Display update requested with changes: {changes}")
        if "battery_icon" in changes:
            asyncio.create_task(self._draw_battery_icon())
        if "noise_player_mode" in changes:
            asyncio.create_task(self._draw_noise_icon())
        if "web_service_status" in changes:
            asyncio.create_task(self._draw_web_service_icon())
        if "time_hour_d1" in changes:
            asyncio.create_task(self._draw_time_h1())
        if "time_hour_d2" in changes:
            asyncio.create_task(self._draw_time_h2())
        if "time_minute_d1" in changes:
            asyncio.create_task(self._draw_time_m1())
        if "time_minute_d2" in changes:
            asyncio.create_task(self._draw_time_m2())
        if "time_am_pm" in changes:
            asyncio.create_task(self._draw_am_pm())
        if "time_day" in changes:
            asyncio.create_task(self._draw_date())


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

    async def _draw_time_h1(self):
        await asyncio.sleep_ms(0)
        if int(self.DISPLAY_CONTEXT.time_hour_d1) < 9:
            await write_font(self.epd, DIGITAL_80_PRE, "!", TIME_CHAR_X1, TIME_CHAR_Y)
        else:
            self.epd.fill_rect(WIFI_ICON_X, 0, 16, 80, 0xff)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_time_h2(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, self.DISPLAY_CONTEXT.time_hour_d2, TIME_CHAR_X2, TIME_CHAR_Y)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_time_div(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, ":", TIME_CHAR_X3, TIME_CHAR_Y)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_time_m1(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, self.DISPLAY_CONTEXT.time_minute_d1, TIME_CHAR_X4, TIME_CHAR_Y)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_time_m2(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, self.DISPLAY_CONTEXT.time_minute_d2, TIME_CHAR_X5, TIME_CHAR_Y)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_am_pm(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, FRANKLIN_18_PRE, self.DISPLAY_CONTEXT.time_am_pm, TIME_CHAR_X6, TIME_CHAR_Y + 64)
        await self.epd.display_Partial(self.epd.buffer)

    async def _draw_date(self):
        await asyncio.sleep_ms(0)
        day_suffix = "$"
        if(self.DISPLAY_CONTEXT.time_day_suffix == "st"):
            day_suffix = "!"
        if(self.DISPLAY_CONTEXT.time_day_suffix == "nd"):
            day_suffix = "@"
        if(self.DISPLAY_CONTEXT.time_day_suffix == "rd"):
            day_suffix = "#"
        
        await write_font(self.epd, FRANKLIN_18_PRE, f"{self.DISPLAY_CONTEXT.time_day_long}, {self.DISPLAY_CONTEXT.time_month_short} {self.DISPLAY_CONTEXT.time_day}{day_suffix}", 0, 110, 296)
        await self.epd.display_Partial(self.epd.buffer)