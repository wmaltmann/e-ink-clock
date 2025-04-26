from PIL import Image

def image_to_bit_array_1d(path):
    # Open the image and convert it to RGB
    image = Image.open(path).convert("RGB")
    
    # Check size
    if image.size != (60, 80):
        raise ValueError("Image must be 60px wide and 80px high (60x80)")

    width, height = image.size
    bit_array = []

    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            bit_array.append(1 if (r, g, b) == (0, 0, 0) else 0)

    return bit_array

# Example usage
bit_array_1d = image_to_bit_array_1d("your_image.png")

# Print first 100 bits
print(bit_array_1d[:100])
