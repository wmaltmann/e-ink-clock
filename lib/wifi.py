import network
import time
from lib.config import Config
from lib.model.log import logger

class Wifi:
    CONTEXT = "WiFi"

    def __init__(self, CONFIG: Config):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)
        self.CONFIG = CONFIG
        self.set_hostname(self.CONFIG.get_network_settings().wifi_hostname)
    
    def set_hostname(self, hostname: str):
        if hostname:
            self.wlan.config(hostname=hostname)
            logger.info(f"Hostname set to: {hostname}", self.CONTEXT)
    
    def connect(self, timeout: int = 30) -> bool:
        self.wlan.active(True)
        if self.is_connected():
            logger.info("Already connected to Wi-Fi", self.CONTEXT)
            return True
        
        available_networks = self.wlan.scan()
        ssid_found = any(net[0].decode('utf-8') == self.CONFIG.get_network_settings().wifi_ssid for net in available_networks)
        
        if not ssid_found:
            logger.error(f"SSID '{self.CONFIG.get_network_settings().wifi_ssid}' not found.", self.CONTEXT)
            return False

        logger.info(f"Connecting to SSID: {self.CONFIG.get_network_settings().wifi_ssid}", self.CONTEXT)
        try:
            self.wlan.connect(self.CONFIG.get_network_settings().wifi_ssid, self.CONFIG.get_network_settings().wifi_password)
            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > timeout:
                    raise Exception("Connection attempt timed out. Check your password.")
                time.sleep(1)
            logger.info("Connected to Wi-Fi", self.CONTEXT)
            logger.info(f"Network config: {self.wlan.ifconfig()}", self.CONTEXT)
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}", self.CONTEXT)
            return False

    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()   # <-- Properly disconnect first
        if self.wlan.active():
            self.wlan.active(False)
        logger.info("Wi-Fi interface disabled", self.CONTEXT)


    def is_connected(self) -> bool:
        return self.wlan.isconnected()

    def ifconfig(self):
        return self.wlan.ifconfig() if self.is_connected() else ""
