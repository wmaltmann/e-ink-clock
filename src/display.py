
import random
from model import epd2in9 as connected_epd


def main():
    epd = connected_epd.EPD()
    print("Initializing display...")
    epd.init()
    print("Setting display to white.")
    epd.clear_frame_memory(0xff)
    epd.display_frame()
    raw_framebuf = bytearray(epd.fb_bytes)
    for pos in range(len(raw_framebuf)):
        raw_framebuf[pos] = 0x00 if random.randint(0, 1) == 0 else 0xff
    print("Displaying random framebuf.")
    
    epd.display_frame_buf(raw_framebuf)
    
    print("Done.")


main()