import ujson
from machine import Pin
from lib.model.display_context import DisplayContext
from lib.clock import Clock
from lib.model.alarm import Alarm
from lib.model.datetime import Datetime
from lib.tone_player import TonePlayer
from lib.noise_player import NoisePlayer
from lib.audio_player import AudioPlayer

try:
    from typing import List
except ImportError:
    pass

class Alarms:
    def __init__(self, display_context: DisplayContext, CLOCK: Clock, TONE_PLAYER: TonePlayer, AUDIO_PLAYER: AudioPlayer, NOISE_PLAYER: NoisePlayer):
        self._TONE_PLAYER = TONE_PLAYER
        self._AUDIO_PLAYER = AUDIO_PLAYER
        self._NOISE_PLAYER = NOISE_PLAYER
        self._pin = Pin(22, Pin.IN, Pin.PULL_UP)
        self.alarm_enabled = self._pin.value() == 0
        self._pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._switch_changed)
        self._CLOCK = CLOCK
        self._DISPLAY_CONTEXT = display_context
        self._alarms = []  # type: list[Alarm]
        self._file_path = "/alarms.json"
        self._load_alarms()
        self._next_alarm = self._get_next_alarm()
        self.alarm_triggered = False
        print(f"Alarm initialized. Enabled: {self.alarm_enabled}")

    def _switch_changed(self, pin):
        if self.alarm_enabled != (pin.value() == 0):
            self.alarm_enabled = pin.value() == 0
            if self.alarm_enabled:    
                self._next_alarm = self._get_next_alarm()
                self._TONE_PLAYER.update_tone(self._next_alarm.frequency if self._next_alarm else 500,
                                             300,
                                             32767 // 4,
                                             50,
                                             1.0,
                                             self._next_alarm.ramp if self._next_alarm else False)
                self._AUDIO_PLAYER.update_audio(300, False) #self._next_alarm.ramp if self._next_alarm else False)
                if self._NOISE_PLAYER.mode == NoisePlayer.MODE_BROWN:
                    #self._NOISE_PLAYER.enable()
                    pass
                self._AUDIO_PLAYER.enable()
                self._DISPLAY_CONTEXT.update_alarm(self.alarm_enabled, self._next_alarm)
            else:
                self.alarm_triggered = False
                self._NOISE_PLAYER.disable()
                self._TONE_PLAYER.disable()
                self._AUDIO_PLAYER.disable()
                self._DISPLAY_CONTEXT.update_alarm(self.alarm_enabled, None)

    def _load_alarms(self):
        try:
            with open(self._file_path, "r") as f:
                data = ujson.load(f)
                self._alarms = [Alarm(**a) for a in data]
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
        now = self._CLOCK.get_time()
        current_day = now.weekday  # 0=Monday, ..., 6=Sunday
        current_minutes = now.hour_24 * 60 + now.minute

        soonest = None
        soonest_delta = float('inf')

        # First pass: look for alarms later today or any day after
        for alarm in self._alarms:
            if not alarm.enabled:
                continue

            for day_offset in range(7):
                check_day = (current_day + day_offset) % 7
                if not alarm.days[check_day]:
                    continue

                alarm_minutes = alarm.hour * 60 + alarm.minute

                # Skip alarms earlier today in first pass
                if day_offset == 0 and alarm_minutes < current_minutes:
                    continue

                delta_minutes = (alarm_minutes - current_minutes) + (day_offset * 1440)

                if delta_minutes < soonest_delta:
                    soonest = alarm
                    soonest_delta = delta_minutes
                    soonest.next_active_day = check_day  # store the day index

        if soonest:
            self._next_alarm = soonest
            return soonest

        # Second pass: allow alarms earlier today (i.e., that occur next week)
        for alarm in self._alarms:
            if not alarm.enabled:
                continue

            check_day = current_day
            if not alarm.days[check_day]:
                continue

            alarm_minutes = alarm.hour * 60 + alarm.minute
            delta_minutes = (alarm_minutes - current_minutes) + (7 * 1440)  # next week's occurrence

            if delta_minutes < soonest_delta:
                soonest = alarm
                soonest_delta = delta_minutes
                soonest.next_active_day = check_day

        self._next_alarm = soonest
        return soonest


    def add_alarm(self, alarm):
        if not isinstance(alarm, Alarm):
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
        if not isinstance(new_alarm, Alarm):
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
    
    def check_alarm(self, now: Datetime):
        """Check if the current time matches the next alarm."""
        if not self.alarm_enabled or self._next_alarm is None:
            pass
        else:
            if (now.weekday == self._next_alarm.next_active_day and
                now.hour_24 == self._next_alarm.hour and
                now.minute == self._next_alarm.minute):

                self.alarm_triggered = True
                if self._next_alarm.tone:
                    self._TONE_PLAYER.enable()
                    print(f"Alarm '{self._next_alarm.name}' tone triggered!")
                elif self._next_alarm.audio:
                    self._AUDIO_PLAYER.enable()
                    print(f"Alarm '{self._next_alarm.name}' audio triggered!")
