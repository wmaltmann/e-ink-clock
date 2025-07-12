import uasyncio as asyncio

class NetworkSettings:
    def __init__(self, wifi_ssid: str = "", password: str = "", hostname: str = "") -> None:
        self.wifi_ssid = wifi_ssid
        self.wifi_password = password
        self.wifi_hostname = hostname


class ClockSettings:
    def __init__(self, clock_display_mode: str = "debug") -> None:
        self.clock_display_mode = clock_display_mode
        self.timezone = "CST"
        self.daylight_saving = True
        self.noise_mode = "None"
        self.noise_volume = 5
        self.timer_volume = 5


class Config:
    """Configuration manager with async, lock‑protected file saves.

    All update* methods schedule an async save task so that configuration
    persistence happens in the background without blocking the caller.
    The save coroutine acquires a lock, writes one line at a time, and
    yields control after each write to minimise CPU hogging on single‑core
    MicroPython boards.
    """

    def __init__(self, filepath: str = "/.config") -> None:
        self.config_filepath = filepath
        self.network = NetworkSettings()
        self.clock = ClockSettings()
        # Lock to serialise file writes
        self._save_lock = asyncio.Lock()
        self._load_config()

    # ──────────────────────────── I/O helpers ────────────────────────────
    def _load_config(self) -> None:
        try:
            with open(self.config_filepath, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        key, value = key.strip(), value.strip()
                        if key == "SSID":
                            self.network.wifi_ssid = value
                        elif key == "PASSWORD":
                            self.network.wifi_password = value
                        elif key == "HOSTNAME":
                            self.network.wifi_hostname = value
                        elif key == "CLOCK_DISPLAY_MODE":
                            self.clock.clock_display_mode = value if value in ("debug", "full_12h", "partial_12h") else "debug"
                        elif key == "NOISE_MODE":
                            self.clock.noise_mode = value if value in ("None", "Brown") else "None"
                        elif key == "NOISE_VOLUME":
                            self.clock.noise_volume = int(value)
                        elif key == "TIMER_VOLUME":
                            self.clock.timer_volume = int(value)
                        elif key == "TIMEZONE":
                            self.clock.timezone = value
                        elif key == "DAYLIGHT_SAVING":
                            self.clock.daylight_saving = True if value.upper() == "TRUE" else False
        except (OSError, ValueError) as e:
            print(f"Error reading config file: {e}")

    async def _save_config(self) -> None:
        """Write current settings to disk serially under a lock.

        Yields to the event loop after each line so the save operation does
        not monopolise the CPU.
        """
        async with self._save_lock:
            try:
                with open(self.config_filepath, "w") as f:
                    f.write(f"SSID={self.network.wifi_ssid}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"PASSWORD={self.network.wifi_password}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"HOSTNAME={self.network.wifi_hostname}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"CLOCK_DISPLAY_MODE={self.clock.clock_display_mode}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"TIMEZONE={self.clock.timezone}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"DAYLIGHT_SAVING={str(self.clock.daylight_saving).upper()}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"NOISE_MODE={self.clock.noise_mode}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"NOISE_VOLUME={self.clock.noise_volume}\n")
                    await asyncio.sleep_ms(10)
                    f.write(f"TIMER_VOLUME={self.clock.timer_volume}\n")
            except OSError as e:
                print(f"Error saving config file: {e}")

    # ──────────────────────────── accessors ──────────────────────────────
    def get_network_settings(self) -> NetworkSettings:
        return self.network

    def get_clock_settings(self) -> ClockSettings:
        return self.clock

    # ──────────────────────────── mutators ───────────────────────────────
    def update_clock_settings(self, clock_display_mode: str) -> None:
        if clock_display_mode not in ("debug", "full_12h", "partial_12h"):
            raise ValueError("Invalid clock mode.")
        self.clock.clock_display_mode = clock_display_mode
        asyncio.create_task(self._save_config())

    def update_noise_mode(self, noise_mode: str) -> None:
        if noise_mode not in ("None", "Brown"):
            raise ValueError("Invalid noise mode.")
        self.clock.noise_mode = noise_mode
        asyncio.create_task(self._save_config())

    def update_network_settings(self, ssid: str, password: str, hostname: str) -> None:
        self.network.wifi_ssid = ssid
        self.network.wifi_password = password
        self.network.wifi_hostname = hostname
        asyncio.create_task(self._save_config())
