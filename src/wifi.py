import network
import ntptime
import time
import machine
from utils.config import load_config

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        time.sleep(1)
    
    print('Connected to Wi-Fi')
    print('Network config:', wlan.ifconfig())

# Function to set system time using NTP
def set_time():
    try:
        ntptime.settime()  # Sync system time with NTP server
        print('Time synchronized with NTP')
    except Exception as e:
        print('Failed to sync time with NTP:', e)

# Function to print current time every second
def print_time():
    while True:
        rtc = machine.RTC()
        current_time = rtc.datetime()  # Get current date and time
        print(f'Time: {current_time[4]}:{current_time[5]}:{current_time[6]}')  # Print hours:minutes:seconds
        time.sleep(1)

# Load Wi-Fi credentials from the config file
config = load_config()

# Check if config was successfully loaded and if SSID/PASSWORD are available
if config:
    SSID = config.get("SSID")
    PASSWORD = config.get("PASSWORD")

    if SSID and PASSWORD:
        connect_wifi(SSID, PASSWORD)
        set_time()

        # Disable Wi-Fi to save power
        network.WLAN(network.STA_IF).active(False)

        # Start printing time
        print_time()
    else:
        print("Error: SSID and/or PASSWORD missing in config file.")
else:
    print("Error: Could not load config file.")
