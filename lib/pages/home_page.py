import socket

def home_page(cl):
    home_html = """
    <html>
    <body>
        <h1>Welcome to the Home Page</h1>
        <p><a href="/alarms">View Alarms</a></p>
        <p><a href="/update_config">Update Config</a></p>
    </body>
    </html>
    """
    
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(home_html)
    cl.close()
