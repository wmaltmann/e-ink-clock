from lib.alarms import Alarms

def view_alarms_page(ALARM: Alarms, cl, request):
    # Create an HTML response with a list of alarms
    alarms_html = """
    <html>
    <body>
        <h1>Alarm List</h1>
        <table border='1'>
            <tr>
                <th>Name</th><th>Time</th><th>Days</th><th>Enabled</th><th>Actions</th>
            </tr>
    """

    for i, alarm in enumerate(ALARM.get_alarms()):
        active_days = ", ".join([
            day for day, active in zip(
                ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], alarm.days
            ) if active
        ])
        time_str = f"{alarm.hour:02}:{alarm.minute:02}"
        enabled_str = "Enabled" if alarm.enabled else "Disabled"

        alarms_html += f"""
            <tr>
                <td>{alarm.name}</td>
                <td>{time_str}</td>
                <td>{active_days}</td>
                <td>{enabled_str}</td>
                <td>
                    <a href="/update_alarm?name={alarm.name}">Update</a> |
                    <a href="/delete_alarm?name={alarm.name}">Delete</a>
                </td>
            </tr>
        """

    alarms_html += """
        </table><br>
        <form action="/add_alarm" method="get">
            <button type="submit">Add New Alarm</button>
        </form>
        <br><a href='/'>Back</a>
    </body>
    </html>
    """

    # Send the HTML response
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(alarms_html)
    cl.close()
