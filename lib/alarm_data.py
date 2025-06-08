class AlarmData:
    def __init__(self, hour: int, minute: int, days, name, next_active_day : int | None = None, enabled=False, vibrate=False, tone=True, ramp=False, frequency=440, hour_12 = 0, am_pm = None):
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 0 and 23")
        if not (0 <= minute <= 59):
            raise ValueError("minute must be between 0 and 59")
        if len(days) != 7 or not all(isinstance(d, bool) for d in days):
            raise ValueError("days must be a list of 7 booleans")

        self.hour = hour
        self.minute = minute
        self.days = days  # List of 7 booleans [Sun, Mon, ..., Sat]
        self.next_active_day = next_active_day
        self.enabled = enabled
        self.vibrate = vibrate
        self.tone = tone
        self.ramp = ramp
        self.frequency = frequency
        self.name = name
        self.hour_12 = self._calc_hour_12() if hour_12 == 0 else hour_12
        self.am_pm = am_pm if am_pm is not None else "AM" if self.hour < 12 else "PM"

    def _calc_hour_12(self):
        h = self.hour % 12
        return 12 if h == 0 else h

    def __str__(self):
        days_str = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        active_days = [days_str[i] for i, active in enumerate(self.days) if active]
        time_str = f"{self.hour:02}:{self.minute:02}"
        return (
            f"Alarm at {time_str} | Enabled: {self.enabled} | Days: {', '.join(active_days)} | "
            f"Vibrate: {self.vibrate} | Tone: {self.tone} | Ramp: {self.ramp} | Freq: {self.frequency}Hz"
        )
