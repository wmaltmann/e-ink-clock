from machine import Pin, I2S
import math
import array
import time
import uasyncio as asyncio

class TonePlayer:
    def __init__(self, frequency=440, duration_sec=4, amplitude=32767 // 4,
                 duty_cycle=100, period=1.0, ramp=False):
        self.frequency = frequency
        self.duration_sec = duration_sec
        self.amplitude = amplitude
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
                await asyncio.sleep(0.1)

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
                current_time = time.ticks_ms()
                elapsed = time.ticks_diff(current_time, start_time)

                if self.ramp and elapsed < ramp_duration_ms:
                    current_amplitude = int(self.amplitude * elapsed / ramp_duration_ms)
                else:
                    current_amplitude = self.amplitude

                sine_wave = array.array("h", [
                    int(current_amplitude * math.sin(2 * math.pi * i / samples_per_cycle))
                    for i in range(samples_per_cycle)
                ])
                stereo_wave = array.array("h", [])
                for sample in sine_wave:
                    stereo_wave.append(sample)
                    stereo_wave.append(sample)

                enable_left.value(1)
                enable_right.value(1)

                if self.duty_cycle > 0:
                    num_cycles_on = int(self.sample_rate * tone_on_time // samples_per_cycle)
                    for _ in range(num_cycles_on):
                        if not self.enabled:
                            break
                        audio.write(stereo_wave)

                if self.duty_cycle < 100 and self.enabled:
                    num_samples_off = int(self.sample_rate * tone_off_time)
                    silence = array.array("h", [0] * num_samples_off * 2)
                    audio.write(silence)
        finally:
            enable_left.value(0)
            enable_right.value(0)
            audio.deinit()
            del audio

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def update_tone(self, frequency=440, duration_sec=300, amplitude=32767 // 4,
                    duty_cycle=100, period=1.0, ramp=False):
        self.frequency = frequency
        self.duration_sec = duration_sec
        self.amplitude = amplitude
        self.duty_cycle = duty_cycle
        self.period = period
        self.ramp = ramp

    def stop(self):
        self._running = False
