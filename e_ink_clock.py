import uasyncio as asyncio
from lib.config import Config
from lib.wifi import Wifi
from lib.clock  import Clock
from lib.display import Display
from lib.alarms  import Alarms
from lib.buttons import Buttons
from lib.nightlight import Nightlight
from lib.battery import Battery
from lib.webservice import WebService
from lib.tone_player import TonePlayer
from lib.noise_player import NoisePlayer
from lib.audio_player import AudioPlayer
from lib.model.display_context import DisplayContext

DISPLAY_CONTEXT = DisplayContext()
CONFIG = Config()
DISPLAY = Display(CONFIG, DISPLAY_CONTEXT)
NIGHTLIGHT = Nightlight()
BATTERY = Battery()
WIFI = Wifi(CONFIG)
CLOCK = Clock(CONFIG, WIFI)
TONE_PLAYER = TonePlayer()
AUDIO_PLAYER = AudioPlayer()
NOISE_PLAYER = NoisePlayer(CONFIG, DISPLAY_CONTEXT)
ALARMS = Alarms(DISPLAY_CONTEXT, CLOCK, TONE_PLAYER, AUDIO_PLAYER, NOISE_PLAYER)
WEB_SERVICE = WebService(WIFI, ALARMS, DISPLAY_CONTEXT)
BUTTONS = Buttons(NIGHTLIGHT, WEB_SERVICE, NOISE_PLAYER, ALARMS)

async def clock_task():
    while True:
        if DISPLAY_CONTEXT.web_service_status != WebService.WEB_SERVICE_ON:
            now = CLOCK.get_time()
            ALARMS.check_alarm(now)
            DISPLAY_CONTEXT.update_time(now)
            sleep_seconds = 60 - now.second
        else:
            sleep_seconds = 60
        await asyncio.sleep(sleep_seconds)

async def battery_monitor_task():
    while True:
        BATTERY.read()
        DISPLAY_CONTEXT.update_battery(BATTERY.voltage, BATTERY.percentage)
        await asyncio.sleep(3600)

async def main():
    await DISPLAY.init()
    CLOCK.set_time_from_ntp()
    asyncio.create_task(TONE_PLAYER.run())
    asyncio.create_task(NOISE_PLAYER.run())
    asyncio.create_task(AUDIO_PLAYER.run())
    asyncio.create_task(WEB_SERVICE.run())
    asyncio.create_task(clock_task())
    asyncio.create_task(battery_monitor_task())
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())