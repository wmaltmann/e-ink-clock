from lib import uuid
from lib.model.alarm import Alarm
from lib.timezone import Timezones
import ujson

def get_alarms(ALARM, cl):
    alarm_list = []
    for a in ALARM.get_alarms():
        alarm_list.append({
            "id": a.id,
            "name": a.name,
            "time": f"{a.hour_12}:{a.minute:02d} {a.am_pm}",
            "days": a.days,
            "enabled": a.enabled
        })
    
    response = ujson.dumps(alarm_list)
    
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
    cl.send(response)
    cl.close()

def get_alarm_page(ALARM, cl, alarm_id: str):
    try:
        alarm = None
        for a in ALARM.get_alarms():
            if a.id == alarm_id:
                alarm = a
                break
        
        if alarm is None:
            response = ujson.dumps({"error": "Alarm not found"})
            cl.send("HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n")
            cl.send(response)
            cl.close()
            return

        alarm_details = {
            "id": alarm.id,
            "hour": alarm.hour_12,
            "minute": alarm.minute,
            "days": alarm.days,
            "name": alarm.name,
            "enabled": alarm.enabled,
            "vibrate": alarm.vibrate,
            "tone": alarm.tone,
            "audio": alarm.audio,
            "ramp": alarm.ramp,
            "frequency": alarm.frequency,
            "am_pm": alarm.am_pm,
            "volume": alarm.volume
        }

        response = ujson.dumps(alarm_details)
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

    except Exception as e:
        response = ujson.dumps({"error": str(e)})
        cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

def update_alarm_param(ALARM, cl, alarm_id: str, param: str, value):
    try:
        alarm = None
        for a in ALARM.get_alarms():
            if a.id == alarm_id:
                alarm = a
                break

        if alarm is None:
            response = ujson.dumps({"error": "Alarm not found"})
            cl.send("HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n")
            cl.send(response)
            cl.close()
            return

        if not hasattr(alarm, param):
            response = ujson.dumps({"error": f"Invalid parameter: {param}"})
            cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n")
            cl.send(response)
            cl.close()
            return

        if param in ["hour", "minute", "frequency", "volume"]:
            value = int(value)
        elif param in ["enabled", "vibrate", "tone", "audio", "ramp"]:
            value = value in ["true", "True", "1", True]

        if param in ["hour", "am_pm"]:
            hour_12 = getattr(alarm, "hour_12", alarm.hour)
            am_pm = getattr(alarm, "am_pm", "AM")

            if param == "hour":
                hour_12 = value
            else:
                am_pm = value

            if am_pm == "AM":
                hour_24 = 0 if hour_12 == 12 else hour_12
            else:
                hour_24 = 12 if hour_12 == 12 else hour_12 + 12

            alarm.hour_12 = hour_12
            alarm.hour = hour_24
            alarm.am_pm = am_pm
        else:
            setattr(alarm, param, value)

        ALARM.save_alarms()

        response = ujson.dumps({"success": True})
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

    except Exception as e:
        response = ujson.dumps({"error": str(e)})
        cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

def create_alarm(ALARM, cl):
    try:
        alarm_id = uuid.generate_uuid()

        new_alarm = Alarm(
            id=alarm_id,
            hour=7,
            minute=0,
            days=[False]*7,
            name="New Alarm",
            enabled=False,
            vibrate=False,
            tone=True,
            audio=False,
            ramp=False,
            frequency=440,
            hour_12=7,
            am_pm="AM",
            volume=10,
        )

        ALARM.add_alarm(new_alarm)

        response = ujson.dumps({"success": True, "alarm_id": alarm_id})
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

    except Exception as e:
        response = ujson.dumps({"error": str(e)})
        cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()


def delete_alarm(ALARM, cl, alarm_id: str):
    try:
        ALARM.remove_alarm(alarm_id)
        response = ujson.dumps({"success": True})
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

    except Exception as e:
        response = ujson.dumps({"error": str(e)})
        cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

def get_timer(TIMER, cl):
    timer_info = {
        "tone": TIMER._tone,
        "vibrate": TIMER._vibrate,
        "audio": TIMER._audio,
        "ramp": TIMER._ramp,
        "frequency": TIMER._frequency,
        "volume": TIMER._volume,
        "intervals": TIMER._intervals
    }
    
    response = ujson.dumps(timer_info)
    
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
    cl.send(response)
    cl.close()

def update_timer_param(TIMER, cl, param: str, value):
    try:
        if not hasattr(TIMER, f"_{param}"):
            response = ujson.dumps({"error": f"Invalid parameter: {param}"})
            cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n")
            cl.send(response)
            cl.close()
            return

        if param in ["frequency", "volume"]:
            value = int(value)
        elif param in ["tone", "vibrate", "audio", "ramp"]:
            value = value in ["true", "True", "1", True]
        elif param == "intervals":
            if isinstance(value, str):
                value = [int(v.strip()) for v in value.split(",")]

        setattr(TIMER, f"_{param}", value)

        TIMER._save_timer()

        response = ujson.dumps({"success": True})
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

    except Exception as e:
        response = ujson.dumps({"error": str(e)})
        cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

def get_config(CONFIG, cl):
    config_info = {
        "ssid": CONFIG.network.wifi_ssid,
        "password": CONFIG.network.wifi_password,
        "hostname": CONFIG.network.wifi_hostname,
        #"clock_display_mode": CONFIG.clock.clock_display_mode,
        "timezone": CONFIG.clock.timezone,
        "daylight": CONFIG.clock.daylight_saving,
        #"noise_mode": CONFIG.clock.noise_mode,
        "volume": CONFIG.clock.noise_volume
    }
    
    response = ujson.dumps(config_info)
    
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
    cl.send(response)
    cl.close()

def update_config_param(CONFIG, cl, param: str, value):
    try:
        # Handle network parameters
        if param == "ssid":
            CONFIG.update_network_settings(value, CONFIG.network.wifi_password, CONFIG.network.wifi_hostname)
        elif param == "password":
            CONFIG.update_network_settings(CONFIG.network.wifi_ssid, value, CONFIG.network.wifi_hostname)
        elif param == "hostname":
            CONFIG.update_network_settings(CONFIG.network.wifi_ssid, CONFIG.network.wifi_password, value)
        # Handle clock parameters
        # elif param == "clock_display_mode":
        #     CONFIG.update_clock_settings(value)
        # elif param == "noise_mode":
        #     CONFIG.update_noise_mode(value)
        elif param == "volume":
            CONFIG.clock.noise_volume = int(value)
            import asyncio
            asyncio.create_task(CONFIG._save_config())
        elif param == "timezone":
            CONFIG.clock.timezone = value
            import asyncio
            asyncio.create_task(CONFIG._save_config())
        elif param == "daylight":
            CONFIG.clock.daylight_saving = value in ["true", "True", "1", True]
            import asyncio
            asyncio.create_task(CONFIG._save_config())
        else:
            response = ujson.dumps({"error": f"Invalid parameter: {param}"})
            cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n")
            cl.send(response)
            cl.close()
            return

        response = ujson.dumps({"success": True})
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

    except Exception as e:
        response = ujson.dumps({"error": str(e)})
        cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n")
        cl.send(response)
        cl.close()

def get_timezone_list(cl):
    timezones_list = []
    for key, value in Timezones.all().items():
        timezones_list.append({
            "short_name": key,
            "name": value["name"]
        })
    
    response = ujson.dumps(timezones_list)
    
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
    cl.send(response)
    cl.close()