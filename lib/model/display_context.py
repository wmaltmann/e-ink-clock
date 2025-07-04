from lib.model.datetime import Datetime
from lib.model.alarm import Alarm

class DisplayContext:
    def __init__(self) -> None:
        self.time_hour_d1 = "0"
        self.time_hour_d2 = "0"
        self.time_minute_d1 = "0"
        self.time_minute_d2 = "0"
        self.time_second_d1 = "0"
        self.time_second_d2 = "0"
        self.time_am_pm = "AM"
        self.time_day = "1"
        self.time_day_short = "Mon"
        self.time_day_long = "Monday"
        self.time_day_suffix = "st"
        self.time_month = "0"
        self.time_month_short = "Jan"
        self.time_month_long = "January"
        self.time_date = "1"
        self.time_year = "2023"
        self.alarm_enabled = False
        self.alarm_next = None
        self.battery_icon = "BATTERY_0"
        self.battery_voltage = 0.0
        self.battery_percentage = 0
        self.web_service_status = ""
        self.message_enabled = False
        self.message_text = ""
        self.noise_player_mode = "None"

        self._subscribers: list = []

    def subscribe(self, callback) -> None:
        self._subscribers.append(callback)

    def _notify_subscribers(self, changed: set[str]) -> None:
        if changed:
            for callback in self._subscribers:
                callback(changed)

    def update_time(self, time: Datetime):
        changed = set()

        hour = f"{time.hour:02}"
        minute = f"{time.minute:02}"
        second = f"{time.second:02}"

        if self.time_hour_d1 != hour[0]:
            self.time_hour_d1 = hour[0]
            changed.add("time_hour_d1")
        if self.time_hour_d2 != hour[1]:
            self.time_hour_d2 = hour[1]
            changed.add("time_hour_d2")
        if self.time_minute_d1 != minute[0]:
            self.time_minute_d1 = minute[0]
            changed.add("time_minute_d1")
        if self.time_minute_d2 != minute[1]:
            self.time_minute_d2 = minute[1]
            changed.add("time_minute_d2")
        if self.time_second_d1 != second[0]:
            self.time_second_d1 = second[0]
            changed.add("time_second_d1")
        if self.time_second_d2 != second[1]:
            self.time_second_d2 = second[1]
            changed.add("time_second_d2")
        if self.time_am_pm != time.am_pm:
            self.time_am_pm = time.am_pm
            changed.add("time_am_pm")
        if self.time_day != time.day:
            self.time_day = time.day
            self.time_day_short = time.day_short
            self.time_day_long = time.day_long
            changed.add("time_day")
        if self.time_month != time.month:
            self.time_month = time.month
            self.time_month_short = time.month_short
            self.time_month_long = time.month_long
            changed.add("time_month")
        if self.time_year != str(time.year):
            self.time_year = str(time.year)
            changed.add("time_year")
        if self.time_day_suffix != time.date_suffix:
            self.time_day_suffix = time.date_suffix
            changed.add("time_day_suffix")
            
        self._notify_subscribers(changed)

    def update_alarm(self, enabled: bool, next_alarm: Alarm | None):
        changed = set()
        if self.alarm_enabled != enabled:
            self.alarm_enabled = enabled
            changed.add("alarm_enabled")
        if self.alarm_next != next_alarm:
            self.alarm_next = next_alarm
            changed.add("alarm_next_alarm")
        self._notify_subscribers(changed)

    def update_battery(self, voltage: float | None = None, percentage: int | None = None):
        changed = set()
        if voltage is not None and self.battery_voltage != voltage:
            self.battery_voltage = voltage
            changed.add("battery_voltage")
        if percentage is not None and self.battery_percentage != percentage:
            self.battery_percentage = percentage
            changed.add("battery_percentage")
            old_icon = self.battery_icon
            if percentage >= 90:
                self.battery_icon = "BATTERY_100"
            elif percentage >= 75:
                self.battery_icon = "BATTERY_75"
            elif percentage >= 50:
                self.battery_icon = "BATTERY_50"
            elif percentage >= 25:
                self.battery_icon = "BATTERY_25"
            else:
                self.battery_icon = "BATTERY_0"
            if self.battery_icon != old_icon:
                changed.add("battery_icon")
        self._notify_subscribers(changed)

    def update_web_service(self, state: str | None = None, message: str | None = None):
        changed = set()
        if state is not None and state != self.web_service_status:
            self.web_service_status = state
            changed.add("web_service_status")
        if message is not None and message != self.message_text:
            if message is "":
                self.message_enabled = False
                self.message_text = ""
            else:
                self.message_enabled
                self.message_text = message
            changed.add("web_service_message")
        self._notify_subscribers(changed)

    def update_noise_player(self, mode: str):
        changed = set()
        if mode != self.noise_player_mode:
            self.noise_player_mode = mode
            changed.add("noise_player_mode")
        self._notify_subscribers(changed)
