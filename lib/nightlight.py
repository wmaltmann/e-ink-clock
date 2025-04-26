from machine import Pin, PWM
from time import ticks_ms

class Nightlight:
    def __init__(self):
        self.led = PWM(Pin(5))
        self.led.freq(1000)
        self.percent = 5
        self.duty_cycle = int((self.percent / 100) * 65535)
        self.timeout = 5000
        self.last_on_time = 0
        
    def on(self, state: bool):
        if state:
            self.last_on_time = ticks_ms()
            self.led.duty_u16(self.duty_cycle)
        else:
            self.led.duty_u16(0)
        
    def set_timeout(self, timeout_ms: int):
        self.timeout = timeout_ms

    def brightness(self, percent: int):
        if 0 <= percent <= 100:
            self.percent = percent
            self.duty_cycle = int((self.percent / 100) * 65535)

    def check_timeout(self):
        if self.led.duty_u16() > 0 and ticks_ms() - self.last_on_time >= self.timeout:
            self.on(False)
