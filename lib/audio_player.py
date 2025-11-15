from machine import Pin, I2S
import time
import uasyncio as asyncio
import struct

class AudioPlayer:
    CHUNK_SIZE = 4096
    SAMPLE_RATE = 8000
    BITS = 16

    def __init__(self, duration_sec=300, ramp=False):
        self.duration_sec = duration_sec
        self.ramp = ramp
        self.fade_in_duration_sec = 30
        self.sample_rate = self.SAMPLE_RATE
        self.bits = self.BITS
        self.enabled = False
        self._running = True
        self.volume_percent = 15

    async def run(self):
        while self._running:
            if self.enabled:
                await self._play_audio_async()
            else:
                await asyncio.sleep_ms(500)

    async def _play_audio_async(self):
        print("Starting audio playback")
        FILENAME = "audio/Glitterati_Melody_Alarm_8000.wav"
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
            def apply_volume(data: bytes, volume_percent: float) -> bytes:
                scale = volume_percent / 100.0
                samples = struct.unpack("<" + "h" * (len(data) // 2), data)
                scaled_samples = [int(s * scale) for s in samples]
                clipped_samples = [max(min(s, 32767), -32768) for s in scaled_samples]
                return struct.pack("<" + "h" * len(clipped_samples), *clipped_samples)

            async def play_wav_file_once_with_fade(filename, fade_in=False):
                with open(filename, "rb") as f:
                    f.read(44)
                    fade_start = time.ticks_ms()
                    while self.enabled:
                        wav_data = f.read(self.CHUNK_SIZE)
                        if not wav_data:
                            break

                        if fade_in:
                            elapsed = time.ticks_diff(time.ticks_ms(), fade_start) / 1000
                            if elapsed < self.fade_in_duration_sec:
                                current_volume = (elapsed / self.fade_in_duration_sec) * self.volume_percent
                            else:
                                current_volume = self.volume_percent
                        else:
                            current_volume = self.volume_percent

                        scaled_data = apply_volume(wav_data, current_volume)
                        audio.write(scaled_data)
                        await asyncio.sleep_ms(0)

            if self.ramp and self.enabled:
                await play_wav_file_once_with_fade(FILENAME, fade_in=True)
            else:
                await play_wav_file_once_with_fade(FILENAME, fade_in=False)

            while self.enabled and time.ticks_ms() < end_time:
                await play_wav_file_once_with_fade(FILENAME, fade_in=False)

        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            print("Stopping audio playback")
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

    def update_audio(self, duration_sec=None, ramp=None, volume_percent=None, fade_in_duration_sec=None):
        if duration_sec is not None:
            self.duration_sec = duration_sec
        if ramp is not None:
            self.ramp = ramp
        if volume_percent is not None:
            self.volume_percent = max(0, min(100, volume_percent))
        if fade_in_duration_sec is not None:
            self.fade_in_duration_sec = max(0, fade_in_duration_sec)
