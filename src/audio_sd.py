from machine import Pin, I2S, SPI
from src.utils.sdcard import SDCard
import uos

# Define I2S pins
SCK_PIN = 1   # BCLK
SD_PIN = 0    # DIN
LRCLK_PIN = 2 # LRCLK

SAMPLE_RATE = 48000
BITS = 16

spi = SPI(0, baudrate=16_000_000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs = Pin(17, Pin.OUT)
sd = SDCard(spi, cs)
vfs = uos.VfsFat(sd) # type: ignore
uos.mount(vfs, "/sd")


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
    ibuf=180000
)

# WAV file playback
FILENAME = "/sd/Glitterati Melody Alarm.wav"
#FILENAME = "src/Glitterati Melody Alarm.wav"
CHUNK_SIZE = 90000  # Bytes per write

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
