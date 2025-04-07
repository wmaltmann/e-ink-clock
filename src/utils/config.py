# config.py

def load_config():
    try:
        with open(".config", "r") as f:
            config = {}
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value

        # Validate SSID and PASSWORD in the config
        SSID = config.get("SSID")
        PASSWORD = config.get("PASSWORD")

        if SSID and PASSWORD:
            return config
        else:
            raise ValueError("Wi-Fi credentials missing in config file.")
        
    except ValueError as e:
        print(f"Error reading config file: {e}")