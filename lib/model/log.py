import utime
import uos


class Log:
    _LEVEL_MAP = {"ERROR": 1, "WARN": 2, "INFO": 3}

    def __init__(self, log_level: str, log_type: str,
                 log_file: str = "/log.txt", max_bytes: int = 51200):
        self._log_level = self._LEVEL_MAP.get(log_level, 1)
        self.log_type = log_type
        self.log_file = log_file
        self.max_bytes = max_bytes
        self.backup_file = log_file + ".1"
        self.info(f"Log initialized with level: {log_level}", "Log")

    def _get_timestamp(self):
        t = utime.localtime()
        return f"{t[1]:02}/{t[2]:02}/{t[0] % 100:02} {t[3]:02}:{t[4]:02}:{t[5]:02}"

    def _rotate(self):
        try:
            size = uos.stat(self.log_file)[6]
        except OSError:
            return  # file doesn't exist yet, nothing to rotate
        if size >= self.max_bytes:
            try:
                uos.remove(self.backup_file)
            except OSError:
                pass  # backup doesn't exist yet
            uos.rename(self.log_file, self.backup_file)

    def _write(self, label: str, message: str, context: str | None):
        timestamp = self._get_timestamp()
        if context:
            line = f"[{timestamp}] [{context}] [{label}] {message}"
        else:
            line = f"[{timestamp}] [{label}] {message}"
        if self.log_type in ("console", "all"):
            print(line)
        if self.log_type in ("file", "all"):
            self._rotate()
            with open(self.log_file, "a") as f:
                f.write(line + "\n")

    def error(self, message: str, context: str | None = None):
        if self._log_level >= 1:
            self._write("ERROR", message, context)

    def warn(self, message: str, context: str | None = None):
        if self._log_level >= 2:
            self._write("WARN", message, context)

    def info(self, message: str, context: str | None = None):
        if self._log_level >= 3:
            self._write("INFO", message, context)


def configure(log_level: str = "ERROR", log_type: str = "console",
              log_file: str = "/log.txt", max_bytes: int = 51200):
    global logger
    logger = Log(log_level, log_type, log_file, max_bytes)


logger = Log(log_level="INFO", log_type="all")
