from machine import Pin, I2S
import array
import time
import uasyncio as asyncio
import random
from lib.config import Config
from lib.model.display_context import DisplayContext

class NoisePlayer():
    MODE_BROWN = "Brown"
    MODE_NONE = "None"
    MODES = [MODE_BROWN, MODE_NONE]

    AMPLITUDE_MAX = 32767  # Max 16-bit signed int

    def __init__(self, CONFIG: Config , display_context: DisplayContext, volume_percent=1, ramp=False):
        self._CONFIG = CONFIG
        self._DISPLAY_CONTEXT = display_context
        self.mode = CONFIG.clock.noise_mode
        self._DISPLAY_CONTEXT.update_noise_player(self.mode)
        self.volume_percent = self._clamp_percent(volume_percent)
        self.ramp = ramp
        self.sample_rate = 8000
        self.bits = 16
        self.enabled = False
        self._running = True
        self._last_output = 0.0  # Persistent state for brown noise continuity

    def _clamp_percent(self, val):
        return max(0, min(100, val))

    async def run(self):
        while self._running:
            if self.enabled:
                if self._CONFIG.clock.noise_mode == self.MODE_BROWN:
                    await self._play_brown_noise_async()
                else:
                    await asyncio.sleep(0.1)   
            else:
                await asyncio.sleep(0.1)

    async def _play_brown_noise_async(self):
        audio = I2S(
            0,
            sck=Pin(1),
            ws=Pin(2),
            sd=Pin(0),
            mode=I2S.TX,
            bits=self.bits,
            format=I2S.STEREO,
            rate=self.sample_rate,
            ibuf=8192*2
        )
        enable_left = Pin(3, Pin.OUT)
        enable_right = Pin(4, Pin.OUT)
        enable_left.value(0)
        enable_right.value(0)

        try:
            ramp_duration_ms = 30000
            start_time = time.ticks_ms()

            while self.enabled:
                current_time = time.ticks_ms()
                elapsed = time.ticks_diff(current_time, start_time)

                if self.ramp and elapsed < ramp_duration_ms:
                    ramp_volume = self.volume_percent * elapsed / ramp_duration_ms
                else:
                    ramp_volume = self.volume_percent

                volume_scale = self._clamp_percent(ramp_volume) / 100

                buffer_size = 4096
                samples = array.array("h")

                for _ in range(buffer_size):
                    white = random.uniform(-1, 1)
                    self._last_output = (self._last_output + (0.02 * white)) / 1.02
                    val = max(-1.0, min(1.0, self._last_output))
                    sample = int(val * self.AMPLITUDE_MAX * volume_scale * 3)
                    samples.append(sample)
                    samples.append(sample)  # stereo

                enable_left.value(1)
                enable_right.value(1)
                audio.write(samples)

                await asyncio.sleep_ms(0)

        finally:
            enable_left.value(0)
            enable_right.value(0)
            audio.deinit()
            del audio

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def stop(self):
        self._running = False

    def update(self, volume_percent=None, ramp=None):
        if volume_percent is not None:
            self.volume_percent = self._clamp_percent(volume_percent)
        if ramp is not None:
            self.ramp = ramp

    def set_mode(self, mode: str):
        if mode in self.MODES:
            self.mode = mode
            self._CONFIG.update_noise_mode(mode)
            self._DISPLAY_CONTEXT.update_noise_player(mode)
        else:
            print(f"Invalid noise mode: {mode}. Valid modes are: {self.MODES}")