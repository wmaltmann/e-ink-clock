import sys
import time
import uasyncio as asyncio
from lib.config import Config
from lib.wifi import Wifi
from lib.clock  import Clock

CONFIG = Config()
WIFI = Wifi(CONFIG)
CLOCK = Clock(WIFI)
print(CLOCK.get_time(),"From system?", CLOCK.get_time_source())

async def clock_task():
    while True:
        # now = time.localtime()
        # seconds_until_next_minute = 60 - now[5]
        # await asyncio.sleep(seconds_until_next_minute + 0.1)
        print(CLOCK.get_time(),"From system?", CLOCK.get_time_source())
        await asyncio.sleep(5)

async def main():
    print("Initializing")
    CLOCK.set_time_from_ntp()
    print("Stating Main Tasks")    
    asyncio.create_task(clock_task())
    await asyncio.sleep(3600)

asyncio.run(main())