import ujson

def get_alarms(ALARM, cl):
    alarm_list = []
    for a in ALARM.get_alarms():
        alarm_list.append({
            "id": a.id,
            "name": a.name,
            "time": f"{a.hour:02d}:{a.minute:02d}",
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
            "hour": alarm.hour,
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

import ujson

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
            response = ujson.dumps({"error": "Invalid parameter: %s" % param})
            cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n")
            cl.send(response)
            cl.close()
            return

        if param in ["hour", "minute", "frequency", "volume"]:
            value = int(value)

        elif param in ["enabled", "vibrate", "tone", "audio", "ramp"]:
            value = True if value in ["true", "True", "1", True] else False

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
