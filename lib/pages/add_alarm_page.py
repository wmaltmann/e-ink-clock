from lib.model.alarm import Alarm

def add_alarm_page(ALARM, cl, request):
    if b"POST /add_alarm" in request:
        try:
            # Extract form data from POST body
            request_str = request.decode()
            body = request_str.split("\r\n\r\n", 1)[1]
            params = dict(param.split("=") for param in body.split("&"))

            hour = int(params.get("hour", 0))
            minute = int(params.get("minute", 0))
            name = params.get("name", "Alarm")
            enabled = params.get("enabled", "off") == "on"
            vibrate = params.get("vibrate", "off") == "on"
            tone = params.get("tone", "off") == "on"
            ramp = params.get("ramp", "off") == "on"
            audio = params.get("audio", "off") == "on"
            frequency = int(params.get("frequency", 440))
            volume = int(params.get("volume",10))

            # Parse days (checkboxes)
            days = [(f"day{i}" in params) for i in range(7)]

            new_alarm = Alarm(
                hour=hour,
                minute=minute,
                days=days,
                name=name,
                enabled=enabled,
                vibrate=vibrate,
                tone=tone,
                ramp=ramp,
                audio=audio,
                frequency=frequency,
                volume = volume
            )

            ALARM.add_alarm(new_alarm)
            response = "<html><body><h2>Alarm added!</h2><a href='/alarms'>Back to alarms</a></body></html>"

        except Exception as e:
            response = f"<html><body><h2>Error adding alarm: {e}</h2><a href='/alarms'>Back</a></body></html>"

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(response)
        cl.close()
        return

    # Show form
    html = """
    <html><body>
    <h1>Add Alarm</h1>
    <form method="POST" action="/add_alarm">
        Name: <input type="text" name="name"><br>
        Hour: <input type="number" name="hour" min="0" max="23"><br>
        Minute: <input type="number" name="minute" min="0" max="59"><br>
        Frequency: <input type="number" name="frequency" value="440"><br>
        Volume: <input type="number" name="volume" value="NA" min="0" max="100"><br>
        <p>Days:</p>
        <label><input type="checkbox" name="day0">Mon</label>
        <label><input type="checkbox" name="day1">Tue</label>
        <label><input type="checkbox" name="day2">Wed</label>
        <label><input type="checkbox" name="day3">Thu</label>
        <label><input type="checkbox" name="day4">Fri</label>
        <label><input type="checkbox" name="day5">Sat</label>
        <label><input type="checkbox" name="day6">Sun</label><br>
        <p>Options:</p>
        <label><input type="checkbox" name="enabled">Enabled</label><br>
        <label><input type="checkbox" name="vibrate">Vibrate</label><br>
        <label><input type="checkbox" name="tone" checked>Tone</label><br>
        <label><input type="checkbox" name="ramp">Ramp</label><br>
        <label><input type="checkbox" name="audio">Audio</label><br>
        <input type="submit" value="Add Alarm">
    </form>
    <br><a href="/alarms">Back to alarms</a>
    </body></html>
    """

    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()
