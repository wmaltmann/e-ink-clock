from lib.clock import Clock

class Log:
    MODE_TEXT = 1
    MODE_CSV = 2

    def __init__(self, filename, mode, clock: Clock):
        if mode not in (self.MODE_TEXT, self.MODE_CSV):
            raise ValueError("Invalid mode. Use Log.MODE_TEXT or Log.MODE_CSV.")
        self.filename = filename
        self.mode = mode
        self.clock = clock

        # Write CSV header if starting a new CSV log
        if self.mode == self.MODE_CSV:
            try:
                with open(self.filename, 'x') as f:
                    f.write("Date,Time,Voltage\n")
            except OSError:
                pass  # File already exists, do not overwrite

    def _get_time_parts(self):
        dt = self.clock.get_time()
        date = f"{dt.month:02}/{dt.day:02}/{dt.year % 100:02}"
        clock = f"{dt.hour_24:02}:{dt.minute:02}:{dt.second:02}"
        return date, clock

    def log(self, message_or_voltage):
        date, clock = self._get_time_parts()

        with open(self.filename, "a") as f:
            if self.mode == self.MODE_TEXT:
                f.write(f"{date}-{clock} : {message_or_voltage}\n")
            elif self.mode == self.MODE_CSV:
                try:
                    voltage = float(message_or_voltage)
                    f.write(f"{date},{clock},{voltage:.3f}\n")
                except ValueError:
                    raise ValueError("CSV mode requires a float-like voltage value.")
