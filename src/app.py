# import time
# import asyncio
from src.model.config import Config
#from src.model.wifi import Wifi
# from src.model.clock import Clock
# from lib.display import Display

CONFIG = Config()

print(CONFIG.network.wifi_ssid)
# DISPLAY = Display()
#WIFI = Wifi(CONFIG)

# async def clock_task():
#     while True:
#         DISPLAY.update_time(CLOCK.get_time())
#         await asyncio.sleep(60)

# async def main():
#     print("Initializing...")
#     CLOCK.set_time_from_ntp()
#     print("Starting Main Tasks")
#     asyncio.create_task(clock_task())

#     # Main loop to keep the program running
#     while True:
#         await asyncio.sleep(60)  # Sleep to keep the loop alive

# asyncio.run(main())
