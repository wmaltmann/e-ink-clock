from machine import Pin
from lib.display import Display
from lib.clock import Clock
class Alarm:
    def __init__(self, DISPLAY: Display, CLOCK: Clock):
        self._pin = Pin(22, Pin.IN, Pin.PULL_UP)
        self.alarm_enabled = self._pin.value() == 0
        self._pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._switch_changed)
        self._CLOCK = CLOCK
        self._DISPLAY = DISPLAY
        print(f"Alarm initialized. Enabled: {self.alarm_enabled}")

    def _switch_changed(self, pin):
        if(self.alarm_enabled != (pin.value() == 0)):
            self.alarm_enabled = pin.value() == 0
            self._DISPLAY.update_alarm(self.alarm_enabled)
            