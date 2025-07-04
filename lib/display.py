import uasyncio as asyncio
from lib.config import Config
from lib.model.queue import Queue
from lib.model.display_context import DisplayContext
from lib.webservice import WebService
from lib.e2in9 import EPD
from lib.font import write_font
from lib.icon import write_icon
from lib.fonts.digital_80_pre import DIGITAL_80_PRE
from lib.fonts.franklin_18_pre import FRANKLIN_18_PRE
from lib.icons.icons_24 import ICONS_24
from lib.profiler import Profiler

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
        self._update_queue = Queue(maxsize=50)
        asyncio.create_task(self._update_runner())

    
    async def init(self):
        await self.epd.init()
        self.epd.reset()
        await self.epd.Clear(0xff)
        self.epd.fill(0xff)
        await self.epd.display(self.epd.buffer)
        await self._draw_time_div()
        self.initialized = True
    
    async def _update_runner(self):
        while True:
            seen_changes = set()
            # Batch changes over a short delay to collapse bursty updates
            try:
                await self._update_queue._get_event.wait()
                await asyncio.sleep_ms(50)
                seen_changes = await self._update_queue.get_all()
            except Exception as e:
                print("Error in update runner:", e)
                continue

            if seen_changes:
                print("Processing display updates:", seen_changes)
            for change in seen_changes:
                if change == "battery_icon":
                    await self._draw_battery_icon()
                elif change == "noise_player_mode":
                    await self._draw_noise_icon()
                elif change == "web_service_status":
                    await self._draw_web_service_icon()
                elif change == "time_hour_d1":
                    await self._draw_time_h1()
                elif change == "time_hour_d2":
                    await self._draw_time_h2()
                elif change == "time_minute_d1":
                    await self._draw_time_m1()
                elif change == "time_minute_d2":
                    Profiler.duration("Display", "draw m1 end")
                    await self._draw_time_m2()
                    Profiler.duration("Display", "draw m2 end")
                elif change == "time_am_pm":
                    await self._draw_am_pm()
                elif change == "time_day":
                    await self._draw_date()
                elif change == "alarm_enabled":
                    await self._draw_alarm()
            
            await asyncio.sleep_ms(0)
            await self.epd.display_Partial(self.epd.buffer)
                    
    def _display_updater(self, changes: set[str]):
        if not self.initialized:
            print("Display not initialized, skipping update.")
            return
        for change in changes:
            try:
                self._update_queue.put_nowait(change)
            except OverflowError:
                print(f"Update queue full, dropped: {change}")

 

#----------------- Asynchronous Drawing Methods -----------------

    async def _draw_battery_icon(self):
        await asyncio.sleep_ms(0)
        write_icon(self.epd, ICONS_24, self.DISPLAY_CONTEXT.battery_icon, BATTERY_ICON_X, 0, 0)
        await asyncio.sleep_ms(0)

    async def _draw_noise_icon(self):
        await asyncio.sleep_ms(0)
        if self.DISPLAY_CONTEXT.noise_player_mode == "Brown":
            write_icon(self.epd, ICONS_24, "WAVE", NOISE_ICON_X, 0, 0)
        else:
            self.epd.fill_rect(NOISE_ICON_X, 0, 24, 24, 0xff)

    async def _draw_web_service_icon(self):
        await asyncio.sleep_ms(0)
        if self.DISPLAY_CONTEXT.web_service_status == WebService.WEB_SERVICE_CONNECTING:
            write_icon(self.epd, ICONS_24, "WIFI_CONFIG", WIFI_ICON_X, 0, 0)
        elif self.DISPLAY_CONTEXT.web_service_status == WebService.WEB_SERVICE_ON:
            write_icon(self.epd, ICONS_24, "WIFI_ON", WIFI_ICON_X, 0, 0)
        else:
            self.epd.fill_rect(WIFI_ICON_X, 0, 24, 24, 0xff)

    async def _draw_time_h1(self):
        await asyncio.sleep_ms(0)
        if int(self.DISPLAY_CONTEXT.time_hour_d1) < 9:
            await write_font(self.epd, DIGITAL_80_PRE, "!", TIME_CHAR_X1, TIME_CHAR_Y)
        else:
            self.epd.fill_rect(WIFI_ICON_X, 0, 16, 80, 0xff)

    async def _draw_time_h2(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, self.DISPLAY_CONTEXT.time_hour_d2, TIME_CHAR_X2, TIME_CHAR_Y)

    async def _draw_time_div(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, ":", TIME_CHAR_X3, TIME_CHAR_Y)

    async def _draw_time_m1(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, self.DISPLAY_CONTEXT.time_minute_d1, TIME_CHAR_X4, TIME_CHAR_Y)

    async def _draw_time_m2(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, DIGITAL_80_PRE, self.DISPLAY_CONTEXT.time_minute_d2, TIME_CHAR_X5, TIME_CHAR_Y)

    async def _draw_am_pm(self):
        await asyncio.sleep_ms(0)
        await write_font(self.epd, FRANKLIN_18_PRE, self.DISPLAY_CONTEXT.time_am_pm, TIME_CHAR_X6, TIME_CHAR_Y + 64)

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

    async def _draw_alarm(self):
        ALARM_ICON_X = 0
        alarm_offset = 0
        if self.DISPLAY_CONTEXT.alarm_enabled:
            alarm_offset = write_icon(self.epd, ICONS_24,"ALARM_ON", ALARM_ICON_X, 0, 0)
            await asyncio.sleep_ms(0)
            alarm_text = ""
            if self.DISPLAY_CONTEXT.alarm_next is None:
                alarm_text = "No Alarm"
            else:
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                next_active_day = "" if self.DISPLAY_CONTEXT.alarm_next.next_active_day is None else days[self.DISPLAY_CONTEXT.alarm_next.next_active_day]
                alarm_text = f"{next_active_day} {self.DISPLAY_CONTEXT.alarm_next.hour_12}:{self.DISPLAY_CONTEXT.alarm_next.minute:02} {self.DISPLAY_CONTEXT.alarm_next.am_pm}"
                self.epd.text(alarm_text, alarm_offset + 4, 8, 0)
            await asyncio.sleep_ms(0)
        else:
            self.epd.fill_rect(0, 0, 180, 24, 0xff)