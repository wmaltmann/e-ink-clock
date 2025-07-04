class Datetime:
    DAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    DAYS_LONG = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    MONTHS_LONG = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    def __init__(self, year, month, day, hour, minute, second, weekday):
        self.DAYS_LONG = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.MONTHS_LONG = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour_24 = int(hour)
        self.minute = int(minute)
        self.second = int(second)
        self.weekday = int(weekday)
        self.day_short = self.DAYS_SHORT[self.weekday % 7]
        self.day_long = self.DAYS_LONG[self.weekday % 7]
        self.month_short = self.MONTHS_SHORT[self.month - 1]
        self.month_long = self.MONTHS_LONG[self.month - 1]
        self.date_suffix = self._get_day_suffix(self.day)
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

    def __rep__(self):
        return (f"{self.year}-{self.month:02}-{self.day:02} "
                f"{self.hour_24:02}:{self.minute:02}:{self.second:02}")

    
    def _get_day_suffix(self, day: int) -> str:
        if 11 <= day % 100 <= 13:
            return "th"
        last_digit = day % 10
        if last_digit == 1:
            return "st"
        elif last_digit == 2:
            return "nd"
        elif last_digit == 3:
            return "rd"
        else:
            return "th"
