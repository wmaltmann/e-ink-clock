from lib.alarms import Alarms

def view_alarms_page(ALARM: Alarms, cl, request):
    # Create an HTML response with responsive CSS
    alarms_html = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: sans-serif;
                padding: 1em;
                font-size: 1em;
            }
            table {
                width: 90%;
                border-collapse: collapse;
            }
            th, td {
                padding: 0.1em 0.1em;
                border: 1px solid #999;
                text-align: left;
                font-size: 0.9em;
            }
            th {
                background-color: #f2f2f2;
            }
            td a {
                font-size: 0.9em;
                display: block;
                margin-bottom: 1em;     
            }
            button {
                font-size: 1em;
                padding: 0.4em 0.8em;
            }
        </style>
    </head>
    <body>
        <h1>Alarm List</h1>
        <table>
            <tr>
                <th>Name</th><th>Time</th><th>Days</th><th>Enabled</th><th>Volume</th><th>Actions</th>
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
                <td>{alarm.volume}</td>
                <td>
                    <a href="/update_alarm?name={alarm.name}">Update</a>
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
