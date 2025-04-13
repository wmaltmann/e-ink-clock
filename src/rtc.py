from machine import I2C, Pin
import utime

# DS3231 I2C address
DS3231_I2C_ADDR = 0x68

# Initialize I2C1 on GP26 (SDA), GP27 (SCL)
i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400000)

def bcd2dec(bcd):
    return (bcd // 16) * 10 + (bcd % 16)

def dec2bcd(dec):
    return (dec // 10) * 16 + (dec % 10)

def get_time():
    data = i2c.readfrom_mem(DS3231_I2C_ADDR, 0x00, 7)
    second = bcd2dec(data[0])
    minute = bcd2dec(data[1])
    hour = bcd2dec(data[2])
    weekday = bcd2dec(data[3])
    day = bcd2dec(data[4])
    month = bcd2dec(data[5] & 0x1F)  # remove century bit
    year = bcd2dec(data[6]) + 2000
    return (year, month, day, weekday, hour, minute, second)

def set_time(year, month, day, weekday, hour, minute, second):
    data = bytearray([
        dec2bcd(second),
        dec2bcd(minute),
        dec2bcd(hour),
        dec2bcd(weekday),
        dec2bcd(day),
        dec2bcd(month),
        dec2bcd(year - 2000)
    ])
    i2c.writeto_mem(DS3231_I2C_ADDR, 0x00, data)

# Example: set time once (only run this once unless you want to reset)

# set_time(2025, 4, 12, 6, 14, 30, 0)  # Sat, April 12, 2025, 14:30:00

print(i2c.scan())
while True:
    t = get_time()
    print("Time: {:04}-{:02}-{:02} {:02} {:02}:{:02}:{:02}".format(*t[:6], t[6]))
    utime.sleep(1)
