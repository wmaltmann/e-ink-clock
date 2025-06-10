from machine import Pin, I2S
import time
import uasyncio as asyncio

class AudioPlayer:
    def __init__(self, duration_sec=300, ramp=False):
        self.duration_sec = duration_sec
        self.ramp = ramp
        self.sample_rate = 48000
        self.bits = 16
        self.audio = I2S(
            0,
            sck=Pin(1),
            ws=Pin(2),
            sd=Pin(0),
            mode=I2S.TX,
            bits=self.bits,
            format=I2S.STEREO,
            rate=self.sample_rate,
            ibuf=40000
        )

        self._enable_left = Pin(3, Pin.OUT)
        self._enable_right = Pin(4, Pin.OUT)
        self._enable_left.value(0)
        self._enable_right.value(0)
        self.enabled = False
        self._running = True

    async def run(self):
        while self._running:
            if self.enabled:
                await self._play_audio_async()
            else:
                await asyncio.sleep(0.1)  # avoid busy waiting

    async def _play_audio_async(self):
        FILENAME = "audio/Glitterati Melody Alarm.wav"
        FADE_FILENAME = "audio/Glitterati Melody Alarm Fade In.wav"
        CHUNK_SIZE = 4144  # Bytes per write
        end_time = time.ticks_ms() + int(self.duration_sec * 1000)

        def play_wav_file_once(filename):
            with open(filename, "rb") as f:
                f.read(44)  # Skip WAV header
                while self.enabled:
                    wav_data = f.read(CHUNK_SIZE)
                    if not wav_data:
                        break
                    self.audio.write(wav_data)

        if self.ramp and self.enabled:
            play_wav_file_once(FADE_FILENAME)

        while self.enabled and time.ticks_ms() < end_time:
            play_wav_file_once(FILENAME)

        self._enable_left.value(0)
        self._enable_right.value(0)

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def update_audio(self, duration_sec=300, ramp=False):
        self.duration_sec = duration_sec
        self.ramp = ramp

    def stop(self):
        self._running = False