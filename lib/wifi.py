import network
import time
from lib.config import Config

class Wifi:
    def __init__(self, CONFIG: Config):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)
        self.CONFIG = CONFIG
    

    def connect(self, timeout: int = 30) -> bool:
        self.wlan.active(True)
        if self.is_connected():
            print("Already connected to Wi-Fi")
            return True

        print(f"Connecting to Wi-Fi SSID: {self.CONFIG.get_network_settings().wifi_ssid}")
        self.wlan.connect(self.CONFIG.get_network_settings().wifi_ssid, self.CONFIG.get_network_settings().wifi_password)

        for _ in range(timeout):
            if self.wlan.isconnected():
                print("Connected to Wi-Fi")
                print("Network config:", self.wlan.ifconfig())
                return True
            time.sleep(1)

        print("Failed to connect to Wi-Fi")
        return False

    def disconnect(self):
        if self.wlan.active():
            self.wlan.active(False)
            print("Wi-Fi interface disabled")

    def is_connected(self) -> bool:
        return self.wlan.isconnected()

    def ifconfig(self):
        return self.wlan.ifconfig() if self.is_connected() else None
