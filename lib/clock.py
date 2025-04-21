import time
from machine import I2C, Pin
import ntptime
from lib.wifi import Wifi
from lib.datetime import DateTime

DS3231_I2C_ADDR = 0x68
TIMEZONE_OFFSET = -6 * 3600  # CST: UTC-6
#TIMEZONE_OFFSET = -5 * 3600  # CDT: UTC-5

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
            return self._get_rtc_time()

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

        # Convert RTC time to seconds since epoch
        utc_tuple = (year, month, day, hour, minute, second, 0, 0)
        epoch_seconds = time.mktime(utc_tuple)

        # Apply timezone offset
        local_time = time.localtime(epoch_seconds + TIMEZONE_OFFSET)

        return DateTime(local_time[0], local_time[1], local_time[2],
                        local_time[3], local_time[4], local_time[5], local_time[6])

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
                ntptime.settime()
                print('Time synchronized with NTP')
                now = time.localtime()
                year, month, day, weekday, hour, minute, second, _ = now
                self._set_rtc_time(year, month, day, weekday, hour, minute, second)
                self.time_source_sys = True
                print("RTC time set from NTP")
                print('Time synchronized with NTP')
                self.WIFI.disconnect()
            except Exception as e:
                print('Failed to sync time with NTP:', e)
                self.time_source_sys = False
                self.WIFI.disconnect()
        
