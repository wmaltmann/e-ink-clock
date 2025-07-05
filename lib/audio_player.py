from machine import Pin, I2S
import time
import uasyncio as asyncio

class AudioPlayer:
    CHUNK_SIZE = 4096
    SAMPLE_RATE = 8000
    BITS = 16

    def __init__(self, duration_sec=300, ramp=False):
        self.duration_sec = duration_sec
        self.ramp = ramp
        self.sample_rate = self.SAMPLE_RATE
        self.bits = self.BITS
        self.enabled = False
        self._running = True
        self.volume_percent = 20  # could be adjusted dynamically

    async def run(self):
        print("Audio Player Running")
        while self._running:
            if self.enabled:
                await self._play_audio_async()
            else:
                await asyncio.sleep(0.1)

    async def _play_audio_async(self):
        print("Audio Player Start")
        FILENAME = "audio/Glitterati_Melody_Alarm_8000.wav"
        FADE_FILENAME = "audio/Glitterati_Melody_Alarm_8000.wav"
        end_time = time.ticks_ms() + int(self.duration_sec * 1000)

        audio = I2S(
            0,
            sck=Pin(1),
            ws=Pin(2),
            sd=Pin(0),
            mode=I2S.TX,
            bits=self.bits,
            format=I2S.STEREO,
            rate=self.sample_rate,
            ibuf=48000
        )
        self.enable_left = Pin(3, Pin.OUT)
        self.enable_right = Pin(4, Pin.OUT)
        self.enable_left.value(1)
        self.enable_right.value(1)

        try:
            def play_wav_file_once(filename):
                with open(filename, "rb") as f:
                    f.read(44)  # skip WAV header
                    while self.enabled:
                        wav_data = f.read(self.CHUNK_SIZE)
                        if not wav_data:
                            break
                        audio.write(wav_data)
                        time.sleep_ms(1)

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
            self.enable_left.value(0)
            self.enable_right.value(0)
            audio.deinit()
            del audio

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def stop(self):
        self._running = False

    def update_audio(self, duration_sec=None, ramp=None, volume_percent=None):
        if duration_sec is not None:
            self.duration_sec = duration_sec
        if ramp is not None:
            self.ramp = ramp
        if volume_percent is not None:
            self.volume_percent = max(0, min(100, volume_percent))
