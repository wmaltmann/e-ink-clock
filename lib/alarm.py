from machine import Pin
from lib.display import Display
from lib.clock import Clock
from lib.alarm_data import AlarmData

class Alarm:
    def __init__(self, DISPLAY: Display, CLOCK: Clock):
        self._pin = Pin(22, Pin.IN, Pin.PULL_UP)
        self.alarm_enabled = self._pin.value() == 0
        self._pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._switch_changed)
        self._CLOCK = CLOCK
        self._DISPLAY = DISPLAY
        self._alarms = []
        print(f"Alarm initialized. Enabled: {self.alarm_enabled}")

    def _switch_changed(self, pin):
        if(self.alarm_enabled != (pin.value() == 0)):
            self.alarm_enabled = pin.value() == 0
            self._DISPLAY.update_alarm(self.alarm_enabled)

    def add_alarm(self, alarm):
        if not isinstance(alarm, AlarmData):
            raise ValueError("alarm must be an Alarm instance")
        self._alarms.append(alarm)

    def remove_alarm(self, index):
        if 0 <= index < len(self._alarms):
            self._alarms.pop(index)

    def list_alarms(self):
        return [str(alarm) for alarm in self._alarms]

    def get_active_alarms_for_day(self, weekday):
        return [alarm for alarm in self._alarms if alarm.enabled and alarm.days[weekday]]