class DateTime:
    def __init__(self, year, month, day, hour, minute, second, weekday=None):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour_24 = int(hour)
        self.minute = int(minute)
        self.second = int(second)
        self.weekday = int(weekday) if weekday is not None else None

        # Determine AM/PM and 12-hour format
        if self.hour_24 == 0:
            self.hour = 12
            self.am_pm = "AM"
        elif self.hour_24 < 12:
            self.hour = self.hour_24
            self.am_pm = "AM"
        elif self.hour_24 == 12:
            self.hour = 12
            self.am_pm = "PM"
        else:
            self.hour = self.hour_24 - 12
            self.am_pm = "PM"

    def string(self):
        return (f"{self.year}-{self.month:02d}-{self.day:02d} {self.hour_24:02d}:{self.minute:02d}:{self.second:02d}")
