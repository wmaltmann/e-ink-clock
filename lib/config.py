# config.py

class NetworkSettings:
    def __init__(self, wifi_ssid="", password="", hostname=""):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = password
        self.wifi_hostname = hostname

class ClockSettings:
    def __init__(self, clock_display_mode="debug"):
        self.clock_display_mode = clock_display_mode
        self.timezone = "CST"
        self.daylight_saving = True
        self.noise_mode = "None"
        self.noise_volume = 5
        self.timer_volume = 5

class Config:
    def __init__(self, filepath="/.config"):
        self.config_filepath = filepath
        self.network = NetworkSettings()
        self.clock = ClockSettings()
        self._load_config()

    def _load_config(self):
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
                            if value in ["debug", "full_12h", "partial_12h"]:
                                self.clock.clock_display_mode = value
                            else:
                                self.clock.clock_display_mode = "debug"
                        elif key == "NOISE_MODE":
                            if value in ["None", "Brown"]:
                                self.clock.noise_mode = value
                            else:
                                self.clock.noise_mode = "None"
                        elif key == "NOISE_VOLUME":
                            self.clock.noise_volume = value
                        elif key == "TIMER_VOLUME":
                            self.clock.timer_volume = value
                        elif key == "TIMEZONE":
                            self.clock.timezone = value
                        elif key == "DAYLIGHT_SAVING":
                            self.clock.daylight_saving = value if value.upper() == "TRUE" else False
        except (OSError, ValueError) as e:
            print(f"Error reading config file: {e}")

    def get_network_settings(self):
        return self.network
    
    def get_clock_settings(self):
        return self.clock
    
    def update_clock_settings(self, clock_display_mode: str):
        if clock_display_mode not in ["debug", "full_12h", "partial_12h"]:
            raise ValueError("Invalid clock mode.")
        self.clock.clock_display_mode = clock_display_mode
        self._save_config()

    def update_noise_mode(self, noise_mode: str):
        if noise_mode not in ["None", "Brown"]:
            raise ValueError("Invalid noise mode.")
        self.clock.noise_mode = noise_mode
        self._save_config()
        
    def update_network_settings(self, ssid: str, password: str, hostname: str):
        self.network.wifi_ssid = ssid
        self.network.wifi_password = password
        self.network.wifi_hostname = hostname
        self._save_config()

    def _save_config(self):
        try:
            with open(self.config_filepath, "w") as f:
                f.write(f"SSID={self.network.wifi_ssid}\n")
                f.write(f"PASSWORD={self.network.wifi_password}\n")
                f.write(f"HOSTNAME={self.network.wifi_hostname}\n")
                f.write(f"CLOCK_DISPLAY_MODE={self.clock.clock_display_mode}\n")
                f.write(f"TIMEZONE={self.clock.timezone}\n")
                f.write(f"DAYLIGHT_SAVING={str(self.clock.daylight_saving).upper()}\n")
                f.write(f"NOISE_MODE={self.clock.noise_mode}\n")
                f.write(f"NOISE_VOLUME={self.clock.noise_volume}\n")
                f.write(f"TIMER_VOLUME={self.clock.timer_volume}\n")
        except OSError as e:
            print(f"Error saving config file: {e}")
