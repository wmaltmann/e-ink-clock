import time
from machine import I2C, Pin
import ntptime
from lib.wifi import Wifi
from lib.datetime import DateTime

DS3231_I2C_ADDR = 0x68
#TIMEZONE_OFFSET = -6 * 3600  # CST: UTC-6
TIMEZONE_OFFSET = -5 * 3600  # CDT: UTC-5

def bcd2dec(bcd):
    return (bcd // 16) * 10 + (bcd % 16)

def dec2bcd(dec):
    return (dec // 10) * 16 + (dec % 10)

class Clock:
    def __init__(self, WIFI: Wifi ):
        self.i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400000)
        self.WIFI = WIFI
        self.time_source_sys = False

    def get_time(self):
        if self.time_source_sys:  
            t = time.localtime(time.time() + TIMEZONE_OFFSET)
            return DateTime(t[0], t[1], t[2], t[3], t[4], t[5], t[6])
        else:
            t = self._get_rtc_time()
            return DateTime(t[0], t[1], t[2], t[3], t[4], t[5], t[6])

    def get_time_source(self):
            return self.time_source_sys
    
    def _get_rtc_time(self):
        data = self.i2c.readfrom_mem(DS3231_I2C_ADDR, 0x00, 7)
        second = bcd2dec(data[0])
        minute = bcd2dec(data[1])
        hour = bcd2dec(data[2])
        weekday = bcd2dec(data[3])
        day = bcd2dec(data[4])
        month = bcd2dec(data[5] & 0x1F)
        year = bcd2dec(data[6]) + 2000

        # Manual offset calculation
        total_seconds = hour * 3600 + minute * 60 + second + TIMEZONE_OFFSET
        if total_seconds < 0 or total_seconds >= 86400:
            # Handle overflow with time.mktime and time.localtime
            from_timestamp = time.mktime((year, month, day, hour, minute, second, 0, 0))
            adjusted = time.localtime(from_timestamp + TIMEZONE_OFFSET)
            return adjusted
        else:
            # Adjust time fields manually
            hour = total_seconds // 3600
            minute = (total_seconds % 3600) // 60
            second = total_seconds % 60
            return (year, month, day, int(hour), int(minute), int(second), weekday, 0)


    def _set_rtc_time(self,year, month, day, weekday, hour, minute, second):
        data = bytearray([
            dec2bcd(second),
            dec2bcd(minute),
            dec2bcd(hour),
            dec2bcd(weekday),
            dec2bcd(day),
            dec2bcd(month),
            dec2bcd(year - 2000)
        ])
        self.i2c.writeto_mem(DS3231_I2C_ADDR, 0x00, data)

    def set_time_from_ntp(self):
        if self.WIFI.connect():
            try:
                ntptime.settime()  # Sets system time in UTC
                print('Time synchronized with NTP')

                # Get UTC time to write to RTC
                now = time.gmtime()
                year, month, day, hour, minute, second, weekday, _ = now

                # weekday returned by gmtime is 0=Monday, DS3231 uses 1=Sunday
                ds3231_weekday = (weekday + 1) % 7 or 7

                self._set_rtc_time(year, month, day, ds3231_weekday, hour, minute, second)
                self.time_source_sys = True
                print("RTC time set from NTP")
                self.WIFI.disconnect()
            except Exception as e:
                print('Failed to sync time with NTP:', e)
                self.time_source_sys = False
                self.WIFI.disconnect()

        
