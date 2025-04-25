from machine import Pin

class Alarm:
    def __init__(self
                 ):
        self._pin = Pin(22, Pin.IN, Pin.PULL_UP)
        self.alarm = self._pin.value() == 0
        self._pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._switch_changed)
        print(f"Alarm initialized. Enabled: {self.alarm}")

    def _switch_changed(self, pin):
        if(self.alarm != (pin.value() == 0)):
            self.alarm = pin.value() == 0
            print("Alarm Enabled: ", self.alarm)