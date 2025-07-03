from lib.alarms import Alarms

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
                params[key] = value.replace("+", " ")
        return params
    except Exception:
        return {}

def delete_alarm_page(ALARM: Alarms, cl, request):
    request_str = request.decode()
    request_line = request_str.split("\r\n", 1)[0]
    query = parse_query_params(request_line)

    name = query.get("name", "")

    try:
        ALARM.remove_alarm(name)
        html = "<html><body><h2>Alarm deleted!</h2><a href='/alarms'>Back to alarms</a></body></html>"
    except ValueError:
        html = "<html><body><h2>Invalid alarm index</h2><a href='/alarms'>Back</a></body></html>"

    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()
