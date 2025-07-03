import framebuf

def write_icon(fb: framebuf.FrameBuffer, icons, icon_name, x_offset, y_offset, width=0):
    if 'height' not in icons or icon_name not in icons:
        return x_offset  # Invalid structure or missing icon

    icon_data = icons[icon_name]
    icon_width = icon_data['width']
    icon_height = icons['height']
    bitmap_hex = icon_data['bitmap']

    bit_array = _hex_string_to_bit_array(bitmap_hex)
    if bit_array is None:
        return x_offset

    if len(bit_array) < icon_width * icon_height:
        raise ValueError(f"Hex string for icon '{icon_name}' does not contain enough bits")

    # Center horizontally in given width if needed
    if width > 0 and icon_width < width:
        x = x_offset + (width - icon_width) // 2
    else:
        x = x_offset

    i = 0
    for y in range(icon_height):
        for dx in range(icon_width):
            bit = bit_array[i]
            fb.pixel(x + dx, y + y_offset, 0x00 if bit == 1 else 0xFF)
            i += 1

    return x + icon_width

def _hex_string_to_bit_array(hex_string):
    bit_array = []
    for i in range(0, len(hex_string), 2):
        byte = int(hex_string[i:i+2], 16)
        for j in range(8):
            bit_array.append((byte >> (7 - j)) & 1)
    return bit_array