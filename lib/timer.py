import ujson as json

class Timer:
    def __init__(self, tone=True, vibrate=False, audio=False, ramp=False,
                 frequency=440, volume=50, intervals=None, interval=5):
        self._tone = tone
        self._vibrate = vibrate
        self._audio = audio
        self._ramp = ramp
        self._frequency = frequency
        self._volume = volume
        self._intervals = intervals or [5, 10, 15, 30, 45, 60]
        self._interval = interval
        self._load_timer()
        self._interval_index = 0

    def update_timer(self, tone=None, vibrate=None, audio=None, ramp=None,
                     frequency=None, volume=None, intervals=None):
        if tone is not None: self._tone = tone
        if vibrate is not None: self._vibrate = vibrate
        if audio is not None: self._audio = audio
        if ramp is not None: self._ramp = ramp
        if frequency is not None: self._frequency = frequency
        if volume is not None: self._volume = volume
        if intervals is not None:
            self._intervals = intervals
            self._interval_index = 0
        self._save_timer()

    def get_interval(self):
        return self._interval
    
    def reset_interval(self):
        self._interval_index = 0
        self._interval = 0
        self._zero_state_returned = False
    
    def toggle_interval(self):
        if self._interval_index < len(self._intervals):
            val = self._intervals[self._interval_index]
            self._interval_index += 1
            self._zero_state_returned = False
            self._interval = val
            return val
        elif not self._zero_state_returned:
            self._zero_state_returned = True
            self._interval_index = 0
            self._interval = 0
            return 0
        else:
            self._interval_index = 0
            self._zero_state_returned = False
            return self.toggle_interval()

    def _load_timer(self):
        try:
            with open("timer.json") as f:
                d = json.load(f)
            self._tone = d.get("tone", self._tone)
            self._vibrate = d.get("vibrate", self._vibrate)
            self._audio = d.get("audio", self._audio)
            self._ramp = d.get("ramp", self._ramp)
            self._frequency = d.get("frequency", self._frequency)
            self._volume = d.get("volume", self._volume)
            self._intervals = d.get("intervals", self._intervals)
            self._interval_index = 0
            self._interval = 5
            print("Timer settings loaded from file.")
        except:
            pass

    def _save_timer(self):
        d = {
            "tone": self._tone,
            "vibrate": self._vibrate,
            "audio": self._audio,
            "ramp": self._ramp,
            "frequency": self._frequency,
            "volume": self._volume,
            "intervals": self._intervals,
        }
        with open("timer.json", "w") as f:
            json.dump(d, f)
