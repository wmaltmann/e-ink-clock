import framebuf

def write_font(fb: framebuf.FrameBuffer, font, text, x_offset, y_offset, width=0):
    height = font['height']

    # First, calculate total width of the text
    text_width = 0
    for char in text:
        if char in font:
            text_width += font[char]['width']

    # Adjust x start position if needed
    if width > 0 and text_width < width:
        x = x_offset + (width - text_width) // 2
    else:
        x = x_offset

    for char in text:
        if char not in font:
            continue  # Skip unknown characters

        char_width = font[char]['width']
        bitmap_hex = font[char]['bitmap']

        bit_array = _hex_string_to_bit_array(bitmap_hex)
        if bit_array is None:
            continue

        if len(bit_array) < char_width * height:
            raise ValueError(f"Hex string for '{char}' does not contain enough bits")

        i = 0
        for y in range(height):
            for dx in range(char_width):
                bit = bit_array[i]
                fb.pixel(x + dx, y + y_offset, 0x00 if bit == 1 else 0xFF)
                i += 1

        x += char_width
    return x



def _hex_string_to_bit_array(hex_string):
    bit_array = []
    for i in range(0, len(hex_string), 2):
        byte = int(hex_string[i:i+2], 16)
        for j in range(8):
            bit_array.append((byte >> (7 - j)) & 1)
    return bit_array