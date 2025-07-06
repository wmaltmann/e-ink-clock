from lib.timezone import Timezones
from lib.config import Config

def parse_form_data(body):
    params = {}
    for pair in body.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value.replace("+", " ")
    return params

def update_config_page(CONFIG: Config, cl, request):
    request_str = request.decode()
    is_post = "POST /update_config" in request_str

    if is_post:
        try:
            body = request_str.split("\r\n\r\n", 1)[1]
            params = parse_form_data(body)

            timezone = params.get("timezone", "CST")
            noise_volume = int(params.get("noise_volume", 5))
            timer_volume = int(params.get("timer_volume", 5))
            daylight = params.get("daylight_saving", "off") == "on"

            CONFIG.clock.timezone = timezone
            CONFIG.clock.noise_volume = noise_volume
            CONFIG.clock.timer_volume = timer_volume
            CONFIG.clock.daylight_saving = daylight
            CONFIG._save_config()

            html = "<html><body><h2>Settings updated!</h2><a href='/'>Back</a></body></html>"
        except Exception as e:
            html = f"<html><body><h2>Error: {e}</h2><a href='/'>Back</a></body></html>"

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()
        return

    current_tz = CONFIG.clock.timezone
    current_noise_volume = CONFIG.clock.noise_volume
    current_timer_volume = getattr(CONFIG.clock, "timer_volume", 5)
    current_dst = CONFIG.clock.daylight_saving

    def selected(key): return "selected" if key == current_tz else ""
    def checked(val): return "checked" if val else ""

    timezone_options = "".join(
        f'<option value="{key}" {selected(key)}>{key} - {val["name"]}</option>'
        for key, val in Timezones.all().items()
    )

    html = f"""
    <html><body>
    <h1>Edit Settings</h1>
    <form method="POST" action="/update_config">
        <label>Timezone:</label><br>
        <select name="timezone">
            {timezone_options}
        </select><br><br>

        <label>Noise Volume:</label><br>
        <input type="number" name="noise_volume" value="{current_noise_volume}" min="0" max="100"><br><br>

        <label>Timer Volume:</label><br>
        <input type="number" name="timer_volume" value="{current_timer_volume}" min="0" max="100"><br><br>

        <label><input type="checkbox" name="daylight_saving" {checked(current_dst)}> Daylight Saving Time</label><br><br>

        <input type="submit" value="Save Settings">
    </form>
    <br><a href="/">Back</a>
    </body></html>
    """

    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()
