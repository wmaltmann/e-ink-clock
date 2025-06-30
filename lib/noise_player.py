from machine import Pin, I2S
import array
import time
import uasyncio as asyncio
import random

class NoisePlayer:
    MODE_BROWN = "Brown"
    MODE_NONE = "None"
    MODES = [MODE_BROWN, MODE_NONE]

    def __init__(self, duration_sec=4, amplitude=32767 // 4, ramp=False):
        self.duration_sec = duration_sec
        self.amplitude = amplitude
        self.ramp = ramp
        self.sample_rate = 4000
        self.bits = 16
        self.enabled = False
        self._running = True

    async def run(self):
        while self._running:
            if self.enabled:
                await self._play_brown_noise_async()
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
            ibuf=20000
        )
        enable_left = Pin(3, Pin.OUT)
        enable_right = Pin(4, Pin.OUT)
        enable_left.value(0)
        enable_right.value(0)

        try:
            ramp_duration_ms = 30000
            start_time = time.ticks_ms()
            end_time = time.ticks_ms() + int(self.duration_sec * 1000)

            last_output = 0.0

            while self.enabled and time.ticks_ms() < end_time:
                current_time = time.ticks_ms()
                elapsed = time.ticks_diff(current_time, start_time)

                if self.ramp and elapsed < ramp_duration_ms:
                    current_amplitude = int(self.amplitude * elapsed / ramp_duration_ms)
                else:
                    current_amplitude = self.amplitude

                # Generate brown noise buffer
                buffer_size = 1024
                samples = array.array("h")
                for _ in range(buffer_size):
                    # Brown noise: low-pass filtered white noise
                    white = random.uniform(-1, 1)
                    last_output = (last_output + (0.02 * white)) / 1.02
                    # Scale and clip to amplitude
                    val = max(-1.0, min(1.0, last_output))
                    sample = int(val * current_amplitude)
                    samples.append(sample)
                    samples.append(sample)  # Stereo

                enable_left.value(1)
                enable_right.value(1)
                audio.write(samples)

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

    def update(self, duration_sec=4, amplitude=32767 // 4, ramp=False):
        self.duration_sec = duration_sec
        self.amplitude = amplitude
        self.ramp = ramp
