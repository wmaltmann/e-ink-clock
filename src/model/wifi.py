import time
import wifi
import ipaddress
from src.model.config import Config

class Wifi:
    def __init__(self, CONFIG: Config):
        self.CONFIG = CONFIG

    def connect(self, timeout: int = 30) -> bool:
        if self.is_connected():
            print("Already connected to Wi-Fi")
            return True

        ssid = self.CONFIG.get_network_settings().wifi_ssid
        password = self.CONFIG.get_network_settings().wifi_password

        print(f"Connecting to Wi-Fi SSID: {ssid}")
        try:
            wifi.radio.connect(ssid, password)
        except Exception as e:
            print("Connection error:", e)
            return False

        for _ in range(timeout):
            if self.is_connected():
                print("Connected to Wi-Fi")
                print("IP address:", wifi.radio.ipv4_address)
                return True
            time.sleep(1)

        print("Failed to connect to Wi-Fi")
        return False

    def disconnect(self):
        try:
            wifi.radio.disconnect()
            print("Wi-Fi disconnected")
        except Exception as e:
            print("Error disconnecting:", e)

    def is_connected(self) -> bool:
        return wifi.radio.connected

    def ifconfig(self):
        if self.is_connected():
            return {
                "ip": str(wifi.radio.ipv4_address),
                "subnet": str(wifi.radio.ipv4_subnet),
                "gateway": str(wifi.radio.ipv4_gateway),
                "dns": str(wifi.radio.ipv4_dns)
            }
        return None
