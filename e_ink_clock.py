import time
import uasyncio as asyncio
from lib.config import Config
from lib.wifi import Wifi
from lib.clock  import Clock
from lib.display import Display

CONFIG = Config()
DISPLAY = Display()
WIFI = Wifi(CONFIG)
CLOCK = Clock(WIFI)

async def clock_task():
    while True:
        DISPLAY.update_time(CLOCK.get_time())
        await asyncio.sleep(60)

async def main():
    print("Initializing")
    CLOCK.set_time_from_ntp()
    print("Stating Main Tasks")    
    asyncio.create_task(clock_task())
    await asyncio.sleep(3600)

asyncio.run(main())