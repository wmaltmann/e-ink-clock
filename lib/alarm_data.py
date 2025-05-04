class AlarmData:
    def __init__(self, hour: int, minute: int, days, name, enabled=False, vibrate=False, tone=True, ramp=False, frequency=440):
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 0 and 23")
        if not (0 <= minute <= 59):
            raise ValueError("minute must be between 0 and 59")
        if len(days) != 7 or not all(isinstance(d, bool) for d in days):
            raise ValueError("days must be a list of 7 booleans")

        self.hour = hour
        self.minute = minute
        self.days = days  # List of 7 booleans [Sun, Mon, ..., Sat]
        self.enabled = enabled
        self.vibrate = vibrate
        self.tone = tone
        self.ramp = ramp
        self.frequency = frequency
        self.name = name

    def __str__(self):
        days_str = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        active_days = [days_str[i] for i, active in enumerate(self.days) if active]
        time_str = f"{self.hour:02}:{self.minute:02}"
        return (
            f"Alarm at {time_str} | Enabled: {self.enabled} | Days: {', '.join(active_days)} | "
            f"Vibrate: {self.vibrate} | Tone: {self.tone} | Ramp: {self.ramp} | Freq: {self.frequency}Hz"
        )
