import socket
import uasyncio as asyncio
from lib.wifi import Wifi
from lib.alarms import Alarms
from lib.model.display_context import DisplayContext
from lib.pages.view_alarms_page import view_alarms_page
from lib.pages.add_alarm_page import add_alarm_page
from lib.pages.update_alarm_page import update_alarm_page
from lib.pages.home_page import home_page
from lib.pages.not_found import not_found_page
from lib.pages.delete_alarm_page import delete_alarm_page

class WebService:
    WEB_SERVICE_ON = "On"
    WEB_SERVICE_OFF = "Off"
    WEB_SERVICE_CONNECTING = "Connecting"
    WEB_SERVICE_STATUS = [
        WEB_SERVICE_ON,
        WEB_SERVICE_OFF,
        WEB_SERVICE_CONNECTING
    ]


    def __init__(self, WIFI: Wifi, ALARM: Alarms, display_context: DisplayContext):
        self.enabled = False
        self._running = True
        self._server_socket = None
        self._ALARM = ALARM
        self._WIFI = WIFI
        self._DISPLAY_CONTEXT = display_context

    async def run(self):
        while self._running:
            if self.enabled:
                await self._serve()
            else:
                await asyncio.sleep_ms(500)

    def enable(self):
        if not self.enabled:
            self._DISPLAY_CONTEXT.update_web_service(self.WEB_SERVICE_CONNECTING,"")
            self._WIFI.connect()
            self.enabled = True
            

    def disable(self):
        if self.enabled:
            self.enabled = False

    def stop(self):
        if self.enabled:
            self.enabled = False
        self._running = False

    async def _serve(self):
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self._server_socket = socket.socket()
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(addr)
        self._server_socket.listen(1)
        self._DISPLAY_CONTEXT.update_web_service(self.WEB_SERVICE_ON, self._WIFI.ifconfig()[0])

        while self.enabled:
            try:
                self._server_socket.settimeout(0.1)
                cl, addr = self._server_socket.accept()
                request = b""
                timeout = False
                while True:
                    try:
                        chunk = cl.recv(1024)
                        if not chunk:
                            break
                        request += chunk
                        if b"\r\n\r\n" in request:
                            break
                    except OSError:
                        timeout = True
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
                    if timeout == False:
                        not_found_page(cl)

            except OSError as e:
                if e.args[0] != 110:  # 110 is ETIMEDOUT
                    print("Socket error:", e)
            except Exception as e:
                print("Error:", e)
            await asyncio.sleep_ms(0)

        if self._server_socket:
            try:
                self._server_socket.close()
            except:
                pass
            self._server_socket = None
            print("Web server stopped")
        self._WIFI.disconnect()
        self._DISPLAY_CONTEXT.update_web_service(self.WEB_SERVICE_OFF,"")

    def http_response(self, cl, body, code=200):
        cl.send(f"HTTP/1.1 {code} OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(body)
        cl.close()
