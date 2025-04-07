# import wifi
# import time
# import socketpool
# import rtc
# import adafruit_ntp
# from utils.config import read_config

# # Read Wi-Fi credentials from the config file
# config = read_config()

# SSID = config.get("SSID")
# PASSWORD = config.get("PASSWORD")


# # Connect to Wi-Fi
# print("Connecting to Wi-Fi...")
# wifi.radio.connect(SSID, PASSWORD)

# # Check if connected
# if wifi.radio.ipv4_address:
#     print(f"Connected to Wi-Fi. IP address: {wifi.radio.ipv4_address}")
# else:
#     print("Failed to connect to Wi-Fi.")

# # Create a socket pool
# pool = socketpool.SocketPool(wifi.radio)

# # Set up NTP client
# ntp = adafruit_ntp.NTP(pool, server="pool.ntp.org", tz_offset=0)  # Set tz_offset as needed

# # Set the RTC (Real-Time Clock) to NTP time
# rtc.RTC().datetime = ntp.datetime
# print("Time synchronized to NTP:", time.localtime())

# # Print time every minute
# while True:
#     current_time = time.localtime()
#     formatted_time = f"{current_time.tm_year:04d}-{current_time.tm_mon:02d}-{current_time.tm_mday:02d}---{current_time.tm_hour:02d}:{current_time.tm_min:02d}:{current_time.tm_sec:02d}"
#     print("Current Time:", formatted_time)

#     time.sleep(60)  # Wait for a minute before printing again