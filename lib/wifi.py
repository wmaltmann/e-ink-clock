import network
import time
from lib.config import Config

class Wifi:
    def __init__(self, CONFIG: Config):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)
        self.CONFIG = CONFIG
        self.set_hostname(self.CONFIG.get_network_settings().wifi_hostname)
    
    def set_hostname(self, hostname: str):
        if hostname:
            self.wlan.config(hostname=hostname)
            print(f"Hostname set to: {hostname}")
    
    def connect(self, timeout: int = 30) -> bool:
        self.wlan.active(True)
        if self.is_connected():
            print("Already connected to Wi-Fi")
            return True
        
        available_networks = self.wlan.scan()
        ssid_found = any(net[0].decode('utf-8') == self.CONFIG.get_network_settings().wifi_ssid for net in available_networks)
        
        if not ssid_found:
            print(f"Error: SSID '{self.CONFIG.get_network_settings().wifi_ssid}' not found.")
            return False

        print(f"Connecting to Wi-Fi SSID: {self.CONFIG.get_network_settings().wifi_ssid}")
        try:
            self.wlan.connect(self.CONFIG.get_network_settings().wifi_ssid, self.CONFIG.get_network_settings().wifi_password)
            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > timeout:
                    raise Exception("Connection attempt timed out. Check your password.")
                time.sleep(1)
            print("Connected to Wi-Fi")
            print("Network config:", self.wlan.ifconfig())
            return True
            
        except Exception as e:
            print(f"Failed to connect to Wi-Fi: {e}")
            return False

    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()   # <-- Properly disconnect first
        if self.wlan.active():
            self.wlan.active(False)
        print("Wi-Fi interface disabled")


    def is_connected(self) -> bool:
        return self.wlan.isconnected()

    def ifconfig(self):
        return self.wlan.ifconfig() if self.is_connected() else ""
