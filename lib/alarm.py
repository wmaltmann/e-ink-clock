import ujson
from machine import Pin
from lib.display import Display
from lib.clock import Clock
from lib.alarm_data import AlarmData

try:
    from typing import List
except ImportError:
    pass

class Alarm:
    def __init__(self, DISPLAY: Display, CLOCK: Clock):
        self._pin = Pin(22, Pin.IN, Pin.PULL_UP)
        self.alarm_enabled = self._pin.value() == 0
        self._pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._switch_changed)
        self._CLOCK = CLOCK
        self._DISPLAY = DISPLAY
        self._alarms = []  # type: list[AlarmData]
        self._file_path = "/alarms.json"
        self._load_alarms()
        self._next_alarm = self._get_next_alarm()
        print(f"Alarm initialized. Enabled: {self.alarm_enabled}")

    def _switch_changed(self, pin):
        if self.alarm_enabled != (pin.value() == 0):
            self.alarm_enabled = pin.value() == 0
            self._DISPLAY.update_alarm(self.alarm_enabled)

    def _load_alarms(self):
        try:
            with open(self._file_path, "r") as f:
                data = ujson.load(f)
                self._alarms = [AlarmData(**a) for a in data]
                print(f"Loaded {len(self._alarms)} alarms from file.")
        except (OSError, ValueError):
            print("No alarm file found or file corrupt. Starting with empty alarm list.")

    def _save_alarms(self):
        try:
            with open(self._file_path, "w") as f:
                ujson.dump([alarm.__dict__ for alarm in self._alarms], f)
                print("Alarms saved.")
        except OSError as e:
            print(f"Failed to save alarms: {e}")
    
    def _get_next_alarm(self):
        now = self._CLOCK.get_time()  # current time as a DateTime instance
        current_day = now.weekday  # 0 = Monday, 6 = Sunday
        current_minutes = now.hour * 60 + now.minute

        soonest = None
        soonest_delta = float('inf')  # Initialize to infinity so any alarm can be smaller

        for alarm in self._alarms:
            if not alarm.enabled:
                continue

            for day_offset in range(7):
                check_day = (current_day + day_offset) % 7
                if not alarm.days[check_day]:
                    continue

                alarm_minutes = alarm.hour * 60 + alarm.minute
                # Compute total minutes to wait
                delta_days = day_offset
                delta_minutes = (alarm_minutes - current_minutes) + (delta_days * 1440)
                if delta_days == 0 and alarm_minutes < current_minutes:
                    continue  # skip alarms earlier today

                if delta_minutes < soonest_delta:
                    soonest = alarm
                    soonest_delta = delta_minutes

        self._next_alarm = soonest
        return soonest

    def add_alarm(self, alarm):
        if not isinstance(alarm, AlarmData):
            raise ValueError("alarm must be an AlarmData instance")
        if not hasattr(alarm, 'name'):
            raise ValueError("alarm must have an 'name' property")
        self._alarms.append(alarm)
        self._save_alarms()

    def remove_alarm(self, name):
        original_count = len(self._alarms)
        self._alarms = [alarm for alarm in self._alarms if alarm.name != name]
        changed = len(self._alarms) < original_count
        if changed:
            self._save_alarms()
        return changed
    
    def update_alarm(self, new_alarm):
        if not isinstance(new_alarm, AlarmData):
            raise ValueError("new_alarm must be an AlarmData instance")
        for i, alarm in enumerate(self._alarms):
            if alarm.name == new_alarm.name:
                self._alarms[i] = new_alarm
                self._save_alarms()
                return True
        return False
    
    def get_alarms(self):
        return self._alarms
    
    def get_alarm(self, name):
        """Return the alarm with the specified name, or None if not found."""
        for alarm in self._alarms:
            if alarm.name == name:
                return alarm
        return None

    
    def get_next_alarm(self):
        self._get_next_alarm()
        return self._next_alarm