import os
import socket
import uasyncio as asyncio  # Use MicroPython's uasyncio instead of threading
from lib.wifi import Wifi
from lib.alarm import Alarm
from lib.display import Display
from lib.pages.view_alarms_page import view_alarms_page
from lib.pages.add_alarm_page import add_alarm_page
from lib.pages.update_alarm_page import update_alarm_page
from lib.pages.home_page import home_page
from lib.pages.not_found import not_found_page
from lib.pages.delete_alarm_page import delete_alarm_page

class WebService:
    def __init__(self, WIFI: Wifi, ALARM: Alarm, DISPLAY: Display):
        self.mode = "Off"
        self._server_socket = None
        self._ALARM = ALARM
        self._WIFI = WIFI
        self._DISPLAY = DISPLAY

    def set_mode(self, mode):
        if mode == "On":
            self._DISPLAY.update_web_service(self._DISPLAY.Web_Service_Connecting)
            self.mode = "On"
            self._WIFI.connect()
            asyncio.create_task(self.start_server())  # Run server asynchronously

        elif mode == "Off":
            self.mode = "Off"
            self.stop_server()
            self._WIFI.disconnect()
            self._DISPLAY.update_web_service(self._DISPLAY.Web_Service_Off)

    async def start_server(self):
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self._server_socket = socket.socket()
        self._server_socket.bind(addr)
        self._server_socket.listen(1)
        print("Web server running")
        self._DISPLAY.update_web_service(self._DISPLAY.Web_Service_On)

        while self.mode == "On":
            try:
                cl, addr = self._server_socket.accept()
                print("Client connected from", addr)
                request = b""
                while True:
                    chunk = cl.recv(1024)
                    if not chunk:
                        break
                    request += chunk
                    if b"\r\n\r\n" in request:
                        break

                if b"GET /alarms" in request:
                    view_alarms_page(self._ALARM, cl, request)
                elif b"GET /add_alarm" in request or b"POST /add_alarm" in request:
                    add_alarm_page(self._ALARM, cl, request)
                elif b"GET /update_alarm" in request or b"POST /update_alarm" in request:
                    update_alarm_page(self._ALARM, cl, request)
                elif b"GET /delete_alarm" in request:
                    delete_alarm_page(self._ALARM, cl, request)    
                elif b"GET /" in request:
                    home_page(cl)
                else:
                    not_found_page(cl)
            except Exception as e:
                print("Error:", e)
            await asyncio.sleep(0)  # Yield control back to the event loop

    def stop_server(self):
        if self._server_socket:
            self._server_socket.close()
            self._server_socket = None
            print("Web server stopped")

    def http_response(self, cl, body, code=200):
        cl.send(f"HTTP/1.1 {code} OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(body)
        cl.close()
