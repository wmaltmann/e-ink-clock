# config.py

class NetworkSettings:
    def __init__(self, wifi_ssid="", password="", hostname=""):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = password
        self.wifi_hostname = hostname


class Config:
    def __init__(self, filepath="/.config"):
        self.config_filepath = filepath
        self.network = NetworkSettings()
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
        except (OSError, ValueError) as e:
            print(f"Error reading config file: {e}")

    def get_network_settings(self):
        return self.network

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
        except OSError as e:
            print(f"Error saving config file: {e}")
