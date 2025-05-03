from lib.datetime import DateTime

class AlarmData:
    def __init__(self, time, days, enabled=True, vibrate=False, tone=False, ramp=False, frequency=440):
        if not isinstance(time, DateTime):
            raise ValueError("time must be a DateTime instance")
        if len(days) != 7 or not all(isinstance(d, bool) for d in days):
            raise ValueError("days must be a list of 7 booleans")

        self.time = time
        self.days = days  # List of 7 booleans [Sun, Mon, ..., Sat]
        self.enabled = enabled
        self.vibrate = vibrate
        self.tone = tone
        self.ramp = ramp
        self.frequency = frequency

    def __str__(self):
        days_str = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        active_days = [days_str[i] for i, active in enumerate(self.days) if active]
        return (
            f"Alarm at {self.time.string()} | Enabled: {self.enabled} | Days: {', '.join(active_days)} | "
            f"Vibrate: {self.vibrate} | Tone: {self.tone} | Ramp: {self.ramp} | Freq: {self.frequency}Hz"
        )
