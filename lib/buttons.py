import time
from machine import Pin
from lib.nightlight import Nightlight
from lib.webservice import WebService
from lib.noise_player import NoisePlayer

class Buttons:
    def __init__(self, NIGHTLIGHT:Nightlight, WEB_SERVICE: WebService, NOISE_PLAYER: NoisePlayer):
        self._button1_pin = Pin(6, Pin.IN, Pin.PULL_UP)
        self._button2_pin = Pin(7, Pin.IN, Pin.PULL_UP)
        self._button3_pin = Pin(14, Pin.IN, Pin.PULL_UP)
        self._button4_pin = Pin(15, Pin.IN, Pin.PULL_UP)
        self._NIGHTLIGHT = NIGHTLIGHT
        self._WEB_SERVICE = WEB_SERVICE
        self._NOISE_PLAYER = NOISE_PLAYER

        self.button1 = self._button1_pin.value() == 0
        self.button2 = self._button2_pin.value() == 0
        self.button3 = self._button3_pin.value() == 0
        self.button4 = self._button4_pin.value() == 0

        self._last_time_button1 = 0
        self._last_time_button2 = 0
        self._last_time_button3 = 0
        self._last_time_button4 = 0

        self._button1_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_1_callback)
        self._button2_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_2_callback)
        self._button3_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_3_callback)
        self._button4_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_4_callback)

        print(f"Buttons initialized. Button states: {self.button1}, {self.button2}, {self.button3}, {self.button4}")

    def _button_1_callback(self, pin: Pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_time_button1) > 50:
            new_state = pin.value() == 0
            if self.button1 != new_state:
                self.button1 = new_state
                print(f"Button 1: {new_state}")
            self._last_time_button1 = now

    def _button_2_callback(self, pin: Pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_time_button2) > 50:
            new_state = pin.value() == 0
            if self.button2 != new_state:
                self.button2 = new_state
                if new_state:
                    if self._NOISE_PLAYER.mode == NoisePlayer.MODE_BROWN:
                        self._NOISE_PLAYER.set_mode(NoisePlayer.MODE_NONE)
                    else:
                        self._NOISE_PLAYER.set_mode(NoisePlayer.MODE_BROWN)
            self._last_time_button2 = now

    def _button_3_callback(self, pin: Pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_time_button3) > 50:
            new_state = pin.value() == 0
            if self.button3 != new_state:
                self.button3 = new_state
                if new_state:
                    if self._WEB_SERVICE.enabled: 
                        self._WEB_SERVICE.disable()
                    else:
                        self._WEB_SERVICE.enable()
            self._last_time_button3 = now

    def _button_4_callback(self, pin: Pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_time_button4) > 50:
            new_state = pin.value() == 0
            if self.button4 != new_state:
                self.button4 = new_state
                if new_state:
                    self._NIGHTLIGHT.on(not self._NIGHTLIGHT.is_on())
            self._last_time_button4 = now
