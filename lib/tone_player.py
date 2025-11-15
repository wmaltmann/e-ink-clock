from machine import Pin, I2S
import math
import array
import time
import uasyncio as asyncio

class TonePlayer:
    MAX_AMPLITUDE = 32767

    def __init__(self, frequency=440, duration_sec=4, volume_percent=25,
                 duty_cycle=100, period=1.0, ramp=False):
        self.frequency = frequency
        self.duration_sec = duration_sec
        self.volume_percent = max(0, min(100, volume_percent))
        self.amplitude = (TonePlayer.MAX_AMPLITUDE * self.volume_percent) // 100

        self.duty_cycle = duty_cycle
        self.period = period
        self.ramp = ramp

        self.sample_rate = 8000
        self.bits = 16

        self.enabled = False
        self._running = True

    async def run(self):
        while self._running:
            if self.enabled:
                await self._play_tone_async()
            else:
                await asyncio.sleep_ms(500)

    async def _play_tone_async(self):
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
            samples_per_cycle = self.sample_rate // self.frequency
            tone_on_time = self.period * (self.duty_cycle / 100)
            tone_off_time = self.period - tone_on_time

            ramp_duration_ms = 30000

            start_time = time.ticks_ms()
            end_time = time.ticks_ms() + int(self.duration_sec * 1000)

            while self.enabled and time.ticks_ms() < end_time:
                current_ms = time.ticks_ms()
                elapsed = time.ticks_diff(current_ms, start_time)

                if self.ramp and elapsed < ramp_duration_ms:
                    current_amplitude = int(self.amplitude * elapsed / ramp_duration_ms)
                else:
                    current_amplitude = self.amplitude

                sine_wave = array.array("h", [
                    int(current_amplitude * math.sin(2 * math.pi * i / samples_per_cycle))
                    for i in range(samples_per_cycle)
                ])

                stereo_wave = array.array("h", [])
                for s in sine_wave:
                    stereo_wave.append(s)
                    stereo_wave.append(s)

                enable_left.value(1)
                enable_right.value(1)

                if self.duty_cycle > 0:
                    cycles_on = int(self.sample_rate * tone_on_time // samples_per_cycle)
                    for _ in range(cycles_on):
                        if not self.enabled:
                            break
                        audio.write(stereo_wave)

                if self.duty_cycle < 100 and self.enabled:
                    off_samples = int(self.sample_rate * tone_off_time)
                    silence = array.array("h", [0] * off_samples * 2)
                    audio.write(silence)

        finally:
            print("Stopping tone playback")
            enable_left.value(0)
            enable_right.value(0)
            audio.deinit()
            del audio

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def update_tone(self, frequency=None, duration_sec=None, volume_percent=None,
                    duty_cycle=None, period=None, ramp=None):

        if frequency is not None:
            self.frequency = frequency

        if duration_sec is not None:
            self.duration_sec = duration_sec

        if volume_percent is not None:
            volume_percent = max(0, min(100, volume_percent))
            self.volume_percent = volume_percent
            self.amplitude = (TonePlayer.MAX_AMPLITUDE * self.volume_percent) // 100

        if duty_cycle is not None:
            self.duty_cycle = duty_cycle

        if period is not None:
            self.period = period

        if ramp is not None:
            self.ramp = ramp

    def stop(self):
        self._running = False
