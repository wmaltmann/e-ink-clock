import machine
import os
import uos
import socket
from sdcard import SDCard

class SDWebService:
    def __init__(self):
        self.mode = "Off"
        self.sd_path = "/sd"
        self.mount_sd()
        self.server_socket = None

    def mount_sd(self):
        spi = machine.SPI(0, baudrate=1_000_000, polarity=0, phase=0,
                          sck=machine.Pin(18),
                          mosi=machine.Pin(19),
                          miso=machine.Pin(16))
        cs = machine.Pin(17, machine.Pin.OUT)
        sd = SDCard(spi, cs)
        vfs = uos.VfsFat(sd)  # type: ignore
        uos.mount(vfs, self.sd_path)

    def set_mode(self, mode):
        if mode == "On":
            self.mode = "On"
            self.start_server()
        elif mode == "Off":
            self.mode = "Off"
            self.stop_server()

    def start_server(self):
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self.server_socket = socket.socket()
        self.server_socket.bind(addr)
        self.server_socket.listen(1)
        print("Web server running on http://0.0.0.0:80")

        while self.mode == "On":
            try:
                cl, addr = self.server_socket.accept()
                print("Client connected from", addr)
                request = b""
                while True:
                    chunk = cl.recv(1024)
                    if not chunk:
                        break
                    request += chunk
                    if b"\r\n\r\n" in request:
                        break

                if b"POST /upload" in request:
                    self.receive_upload(cl, request)
                elif b"GET /download?file=" in request:
                    self.send_download(cl, request.decode())
                elif b"GET / " in request:
                    self.send_file_list(cl)
                else:
                    self.http_response(cl, "Invalid request", 400)
            except Exception as e:
                print("Error:", e)

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            print("Web server stopped")

    def send_file_list(self, cl):
        files = os.listdir(self.sd_path)
        body = "<h1>Files on SD</h1><ul>"
        for f in files:
            body += f'<li><a href="/download?file={f}">{f}</a></li>'
        body += "</ul>"
        body += '''
            <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
            </form>
        '''
        self.http_response(cl, body)

    def send_download(self, cl, request):
        try:
            path = request.split("GET /download?file=")[1].split(" ")[0]
            filepath = f"{self.sd_path}/{path}"
            if path not in os.listdir(self.sd_path):
                self.http_response(cl, "File not found", 404)
                return
            cl.send("HTTP/1.1 200 OK\r\n")
            cl.send("Content-Type: application/octet-stream\r\n\r\n")
            with open(filepath, "rb") as f:
                while True:
                    data = f.read(512)
                    if not data:
                        break
                    cl.send(data)
        except Exception as e:
            self.http_response(cl, f"Error: {e}", 500)
        finally:
            cl.close()

    def receive_upload(self, cl, request_bytes):
        try:
            request_str = request_bytes.decode(errors="ignore")
            content_start = request_str.find("\r\n\r\n") + 4
            headers = request_str[:content_start]

            # Extract boundary
            boundary = None
            for line in headers.split("\r\n"):
                if "Content-Type: multipart/form-data" in line:
                    boundary = line.split("boundary=")[-1].strip()
                    break
            if not boundary:
                self.http_response(cl, "Boundary not found", 400)
                return

            boundary = "--" + boundary
            body = request_bytes[content_start:]

            # Find start and end of file content
            parts = body.split(boundary.encode())
            for part in parts:
                if b"Content-Disposition" in part:
                    header_end = part.find(b"\r\n\r\n") + 4
                    header = part[:header_end].decode(errors="ignore")
                    content = part[header_end:-2]  # Remove trailing \r\n

                    # Get filename
                    filename = "upload.bin"
                    if "filename=" in header:
                        filename = header.split("filename=")[1].split("\r\n")[0]
                        filename = filename.strip('"').strip()

                    filepath = f"{self.sd_path}/{filename}"
                    with open(filepath, "wb") as f:
                        f.write(content)

                    self.http_response(cl, f"<p>Upload successful: {filename}</p><a href='/'>Back</a>")
                    return

            self.http_response(cl, "No file uploaded", 400)

        except Exception as e:
            self.http_response(cl, f"Upload error: {e}", 500)


    def http_response(self, cl, body, code=200):
        cl.send(f"HTTP/1.1 {code} OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(body)
        cl.close()
