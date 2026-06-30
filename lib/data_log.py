from lib.clock import Clock


class DataLog:

    def __init__(self, filename, clock: Clock):
        self.filename = filename
        self.clock = clock

        try:
            with open(self.filename, 'x') as f:
                f.write("timestamp,key,value\n")
        except OSError:
            pass  # File already exists, do not overwrite

    def _get_timestamp(self):
        dt = self.clock.get_time()
        return f"{dt.month:02}/{dt.day:02}/{dt.year % 100:02} {dt.hour_24:02}:{dt.minute:02}:{dt.second:02}"

    def data_log(self, key, value):
        timestamp = self._get_timestamp()
        with open(self.filename, "a") as f:
            f.write(f"{timestamp},{key},{value}\n")