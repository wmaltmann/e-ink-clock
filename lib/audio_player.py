from machine import Pin, I2S
import time
import uasyncio as asyncio

class AudioPlayer:
    def __init__(self, duration_sec=300, ramp=False):
        self.duration_sec = duration_sec
        self.ramp = ramp
        self.sample_rate = 48000
        self.bits = 16
        self.enabled = False
        self._running = True

    async def run(self):
        while self._running:
            if self.enabled:
                await self._play_audio_async()
            else:
                await asyncio.sleep(0.1)

    async def _play_audio_async(self):
        FILENAME = "audio/Glitterati Melody Alarm.wav"
        FADE_FILENAME = "../audio/Glitterati Melody Alarm Fade In.wav"
        CHUNK_SIZE = 4144
        end_time = time.ticks_ms() + int(self.duration_sec * 1000)

        # Reserve I2S and pins
        audio = I2S(
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
        enable_left = Pin(3, Pin.OUT)
        enable_right = Pin(4, Pin.OUT)
        print("Audio Player initialized.")
        try:
            enable_left.value(1)
            enable_right.value(1)

            def play_wav_file_once(filename):
                with open(filename, "rb") as f:
                    f.read(44)  # Skip WAV header
                    while self.enabled:
                        wav_data = f.read(CHUNK_SIZE)
                        if not wav_data:
                            break
                        audio.write(wav_data)

            if self.ramp and self.enabled:
                print("Playing fade-in audio.")
                play_wav_file_once(FADE_FILENAME)

            while self.enabled and time.ticks_ms() < end_time:
                print("Playing main audio.")
                play_wav_file_once(FILENAME)
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            print("Stopping audio playback.")
            enable_left.value(0)
            enable_right.value(0)
            audio.deinit()
            del audio

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def update_audio(self, duration_sec=300, ramp=False):
        self.duration_sec = duration_sec
        self.ramp = ramp

    def stop(self):
        self._running = False
