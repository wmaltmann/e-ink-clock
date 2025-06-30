import uasyncio as asyncio
from lib.config import Config
from lib.wifi import Wifi
from lib.clock  import Clock
from lib.display import Display
from lib.alarm  import Alarm
from lib.buttons import Buttons
from lib.nightlight import Nightlight
from lib.battery import Battery
from lib.webservice import WebService
from lib.tone_player import TonePlayer
from lib.noise_player import NoisePlayer
from lib.audio_player import AudioPlayer

CONFIG = Config()
DISPLAY = Display(CONFIG)
NIGHTLIGHT = Nightlight()
BATTERY = Battery()
WIFI = Wifi(CONFIG)
CLOCK = Clock(CONFIG, WIFI)
TONE_PLAYER = TonePlayer()
AUDIO_PLAYER = AudioPlayer()
NOISE_PLAYER = NoisePlayer()
ALARM = Alarm(DISPLAY, CLOCK, TONE_PLAYER, AUDIO_PLAYER, NOISE_PLAYER)
WEB_SERVICE = WebService(WIFI, ALARM, DISPLAY)
BUTTONS = Buttons(NIGHTLIGHT, WEB_SERVICE)

async def clock_task():
    while True:
        now = CLOCK.get_time()
        ALARM.check_alarm(now)
        DISPLAY.update_time(now)
        sleep_seconds = 60 - now.second
        await asyncio.sleep(sleep_seconds)

async def battery_monitor_task():
    while True:
        BATTERY.read()
        DISPLAY.update_battery(BATTERY.voltage, BATTERY.percentage)
        await asyncio.sleep(3600)

async def main():
    CLOCK.set_time_from_ntp()
    asyncio.create_task(TONE_PLAYER.run())
    asyncio.create_task(NOISE_PLAYER.run())
    asyncio.create_task(WEB_SERVICE.run())
    asyncio.create_task(clock_task())
    asyncio.create_task(battery_monitor_task())
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())