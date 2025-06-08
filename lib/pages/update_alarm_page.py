from lib.alarm_data import AlarmData
from lib.alarm import Alarm

def unescape_text(text):
    result = ""
    i = 0
    while i < len(text):
        if text[i] == '%' and i + 2 < len(text):
            try:
                hex_value = text[i+1:i+3]
                result += chr(int(hex_value, 16))
                i += 3
            except ValueError:
                result += text[i]
                i += 1
        else:
            result += text[i]
            i += 1
    return result

def parse_query_params(request_line):
    try:
        parts = request_line.split(" ")
        if len(parts) < 2:
            return {}

        path = parts[1]
        if "?" not in path:
            return {}

        _, query_string = path.split("?", 1)
        params = {}
        for pair in query_string.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                key = unescape_text(key.replace("+", " "))
                value = unescape_text(value.replace("+", " "))
                params[key] = value
        return params
    except Exception as e:
        print("Query parse error:", e)
        return {}

def parse_form_data(body):
    params = {}
    for pair in body.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value.replace("+", " ")
    return params

def update_alarm_page(ALARM: Alarm , cl, request):
    request_str = request.decode()
    request_line = request_str.split("\r\n", 1)[0]
    query = parse_query_params(request_line)
    name = query.get("name", "")
    print("Update alarm request for:", name)
    alarm = ALARM.get_alarm(name)

    if alarm is None:
        cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
        cl.send("<html><body><h2>Invalid alarm index</h2><a href='/alarms'>Back</a></body></html>")
        cl.close()
        return

    is_post = "POST /update_alarm" in request_str

    if is_post:
        try:
            body = request_str.split("\r\n\r\n", 1)[1]
            params = parse_form_data(body)

            updated_alarm = AlarmData(
                hour=int(params.get("hour", 0)),
                minute=int(params.get("minute", 0)),
                days=[(f"day{i}" in params) for i in range(7)],
                name=params.get("name", "Alarm"),
                enabled=params.get("enabled", "off") == "on",
                vibrate=params.get("vibrate", "off") == "on",
                tone=params.get("tone", "off") == "on",
                ramp=params.get("ramp", "off") == "on",
                frequency=int(params.get("frequency", 440))
            )

            ALARM.update_alarm(updated_alarm)
            html = "<html><body><h2>Alarm updated!</h2><a href='/alarms'>Back to alarms</a></body></html>"

        except Exception as e:
            html = f"<html><body><h2>Error: {e}</h2><a href='/alarms'>Back</a></body></html>"

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()
        return

    def checked(cond): return "checked" if cond else ""

    html = f"""
    <html><body>
    <h1>Edit Alarm</h1>
    <form method="POST" action="/update_alarm?name={alarm.name}">
        Name: <input type="text" name="name" value="{alarm.name}"><br>
        Hour: <input type="number" name="hour" min="0" max="23" value="{alarm.hour}"><br>
        Minute: <input type="number" name="minute" min="0" max="59" value="{alarm.minute}"><br>
        Frequency: <input type="number" name="frequency" value="{alarm.frequency}"><br>
        <p>Days:</p>
    """
    for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        html += f'<label><input type="checkbox" name="day{i}" {checked(alarm.days[i])}>{day}</label> '

    html += f"""
        <p>Options:</p>
        <label><input type="checkbox" name="enabled" {checked(alarm.enabled)}>Enabled</label><br>
        <label><input type="checkbox" name="vibrate" {checked(alarm.vibrate)}>Vibrate</label><br>
        <label><input type="checkbox" name="tone" {checked(alarm.tone)}>Tone</label><br>
        <label><input type="checkbox" name="ramp" {checked(alarm.ramp)}>Ramp</label><br>
        <input type="submit" value="Update Alarm">
    </form>
    <br><a href="/alarms">Back to alarms</a>
    </body></html>
    """

    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()
