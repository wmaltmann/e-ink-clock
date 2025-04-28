import uasyncio as asyncio
from lib.config import Config
from lib.wifi import Wifi
from lib.clock  import Clock
from lib.display import Display
from lib.alarm  import Alarm
from lib.buttons import Buttons
from lib.nightlight import Nightlight
from lib.battery import Battery

CONFIG = Config()
DISPLAY = Display()
NIGHTLIGHT = Nightlight()
BATTERY = Battery()
BUTTONS = Buttons(NIGHTLIGHT)
WIFI = Wifi(CONFIG)
CLOCK = Clock(WIFI)
ALARM = Alarm(DISPLAY, CLOCK)


async def clock_task():
    while True:
        now = CLOCK.get_time()
        DISPLAY.update_time(now)
        sleep_seconds = 60 - now.second
        await asyncio.sleep(sleep_seconds)

async def battery_monitor_task():
    while True:
        BATTERY.read()
        DISPLAY.update_battery(BATTERY.voltage, BATTERY.percentage)
        await asyncio.sleep(3600)

async def main():
    print("Initializing")
    CLOCK.set_time_from_ntp()
    print("Stating Main Tasks")    
    asyncio.create_task(clock_task())
    asyncio.create_task(battery_monitor_task())
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())