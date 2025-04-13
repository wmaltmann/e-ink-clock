from machine import Pin, I2C
import time

# Use I2C1 on GP27 (SDA), GP26 (SCL)
i2c1 = I2C(1, scl=Pin(27), sda=Pin(26))

accel_addr = 0x69

print(i2c1.scan())

def wake_up_accel(i2c: I2C):
    i2c.writeto(accel_addr, bytes([0x6B, 0x00]))

def bytes_to_int(high, low):
    value = (high << 8) | low
    if value & 0x8000:
        value -= 65536
    return value

def read_accel(i2c: I2C):
        # Read 6 bytes starting from ACCEL_XOUT_H (0x3B)
        i2c.writeto(accel_addr, bytes([0x3B]))
        data = i2c.readfrom(accel_addr, 6)

        accel_x = bytes_to_int(data[0], data[1])
        accel_y = bytes_to_int(data[2], data[3])
        accel_z = bytes_to_int(data[4], data[5])

        return (
            accel_x / 16384.0,
            accel_y / 16384.0,
            accel_z / 16384.0
        )


# start
wake_up_accel(i2c1)

while True:
    x, y, z = read_accel(i2c1)
    print("Accel X: {:.2f} g, Y: {:.2f} g, Z: {:.2f} g".format(x, y, z))
    time.sleep(1)
