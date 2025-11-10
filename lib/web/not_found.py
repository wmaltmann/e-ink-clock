def not_found_page(cl):
    home_html = """
    <html>
    <body>
        <h1>Page Not found</h1>
        <br><a href="/">Back to home</a>
    </body>
    </html>
    """
    
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(home_html)
    cl.close()
