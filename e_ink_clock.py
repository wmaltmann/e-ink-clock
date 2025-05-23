import uasyncio as asyncio
from lib.config import Config
from lib.wifi import Wifi
from lib.clock  import Clock
from lib.display import Display
from lib.alarm  import Alarm
from lib.buttons import Buttons
from lib.nightlight import Nightlight
from lib.battery import Battery
from lib.log import Log
from lib.webservice import WebService

CONFIG = Config()
DISPLAY = Display(CONFIG)
NIGHTLIGHT = Nightlight()
BATTERY = Battery()
WIFI = Wifi(CONFIG)
CLOCK = Clock(WIFI)
BATTERY_LOG = Log("battery_level.csv", Log.MODE_CSV, CLOCK)
ALARM = Alarm(DISPLAY, CLOCK)
WEB_SERVICE = WebService(WIFI, ALARM, DISPLAY)
BUTTONS = Buttons(NIGHTLIGHT, WEB_SERVICE)

async def clock_task():
    while True:
        now = CLOCK.get_time()
        DISPLAY.update_time(now)
        sleep_seconds = 60 - now.second
        await asyncio.sleep(sleep_seconds)

async def battery_monitor_task():
    while True:
        BATTERY.read()
        BATTERY_LOG.log(BATTERY.voltage)
        DISPLAY.update_battery(BATTERY.voltage, BATTERY.percentage)
        await asyncio.sleep(300)

async def main():
    print("Initializing")
    CLOCK.set_time_from_ntp()
    print("Stating Main Tasks")    
    asyncio.create_task(clock_task())
    asyncio.create_task(battery_monitor_task())
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())