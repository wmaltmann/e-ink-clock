import asyncio
import framebuf

async def write_font(fb: framebuf.FrameBuffer, font, text, x_offset, y_offset, width=0):
    height = font['height']
    # Calculate total text width for centering if width > 0
    text_width = sum(font[c]['width'] for c in text if c in font)

    # Calculate starting x position (center if possible)
    x = x_offset + ((width - text_width) // 2) if width > 0 and text_width < width else x_offset

    # Draw each character
    for char in text:
        if char not in font:
            continue  # skip unknown characters

        bitmap = font[char]['bitmap_bytes']
        char_width = font[char]['width']

        bit_index = 0
        for y in range(height):
            for dx in range(char_width):
                byte_index = bit_index // 8
                bit_pos = 7 - (bit_index % 8)
                bit = (bitmap[byte_index] >> bit_pos) & 1
                # Draw pixel: 0x00 for set (black), 0xFF for unset (white)
                fb.pixel(x + dx, y + y_offset, 0x00 if bit else 0xFF)
                bit_index += 1
        await asyncio.sleep_ms(0)
        x += char_width  # move x for next character


    return x
