class DateTime:
    def __init__(self, year, month, day, hour, minute, second, weekday=None):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.weekday = weekday

    def __repr__(self):
        return (f"DateTime({self.year}-{self.month:02}-{self.day:02} "
                f"{self.hour:02}:{self.minute:02}:{self.second:02})")
