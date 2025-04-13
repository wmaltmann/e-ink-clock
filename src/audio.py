from machine import Pin, I2S, PWM
import os

# Define I2S pins
SCK_PIN = 1   # BCLK
SD_PIN = 0    # DIN
LRCLK_PIN = 2 # LRCLK

SAMPLE_RATE = 48000
BITS = 16

# Enable I2S amplifier output or mux

Enable_Left = Pin(3, Pin.OUT)
Enable_Right = Pin(4, Pin.OUT)
Enable_Left.value(1)
Enable_Right.value(1)


# Setup I2S interface
audio = I2S(
    0,
    sck=Pin(SCK_PIN),
    ws=Pin(LRCLK_PIN),
    sd=Pin(SD_PIN),
    mode=I2S.TX,
    bits=16,
    format=I2S.STEREO,
    rate=SAMPLE_RATE,
    ibuf=40000
)

# WAV file playback
FILENAME = "src/Glitterati Melody Alarm.wav"
#FILENAME = "src/side-to-side-8k-16bits-stereo.wav"
CHUNK_SIZE = 4144  # Bytes per write

try:
    with open(FILENAME, "rb") as f:
        # Skip WAV header (usually 44 bytes)
        f.read(44)

        print("Playing", FILENAME)

        while True:
            wav_data = f.read(CHUNK_SIZE)
            if not wav_data:
                break
            audio.write(wav_data)


except KeyboardInterrupt:
    pass
except Exception as e:
    print("Error:", e)
finally:
    audio.deinit()

    print("Playback stopped.")
