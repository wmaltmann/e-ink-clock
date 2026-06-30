import socket
import ujson
import gc
import uasyncio as asyncio
from lib.wifi import Wifi
from lib.alarms import Alarms
from lib.model.display_context import DisplayContext
from lib.config import Config
from lib.timer import Timer
from lib.model.log import logger
from lib.web.api import create_alarm, delete_alarm, get_alarm_page, get_alarms, get_config, get_log, get_timer, get_timezone_list, update_alarm_param, update_config_param, update_timer_param


class WebService:
    WEB_SERVICE_ON = "On"
    WEB_SERVICE_OFF = "Off"
    WEB_SERVICE_CONNECTING = "Connecting"
    WEB_SERVICE_STATUS = [
        WEB_SERVICE_ON,
        WEB_SERVICE_OFF,
        WEB_SERVICE_CONNECTING
    ]
    CONTEXT = "WebService"


    def __init__(self, WIFI: Wifi, ALARM: Alarms, display_context: DisplayContext, config: Config, TIMER: Timer):
        self.enabled = False
        self._running = True
        self._server_socket = None
        self._ALARM = ALARM
        self._WIFI = WIFI
        self._DISPLAY_CONTEXT = display_context
        self._CONFIG = config
        self._TIMER = TIMER

    async def run(self):
        while self._running:
            if self.enabled:
                await self._serve()
            else:
                await asyncio.sleep_ms(500)

    def enable(self):
        if not self.enabled:
            asyncio.create_task(self._async_enable())

    async def _async_enable(self):
        if not self.enabled:
            logger.info("Enabling web service...", self.CONTEXT)
            self._DISPLAY_CONTEXT.update_web_service(self.WEB_SERVICE_CONNECTING,"")
            await asyncio.sleep_ms(1000)
            logger.info("Connecting to WiFi...", self.CONTEXT)
            self._WIFI.connect()
            self._DISPLAY_CONTEXT.update_web_service(self.WEB_SERVICE_ON, self._WIFI.ifconfig()[0])
            await asyncio.sleep_ms(1000)
            logger.info("Starting web server...", self.CONTEXT)
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
        
        while self.enabled:
            cl = None
            request = None
            try:
                self._server_socket.settimeout(1)
                cl, addr = self._server_socket.accept()
                request = b""
                while True:
                    try:
                        chunk = cl.recv(1024)
                        if not chunk:
                            break
                        request += chunk
                        if b"\r\n\r\n" in request:
                            break
                    except OSError:
                        break

                if b"POST /api/alarms/create" in request:
                    logger.info("Serving: POST api/alarms/create", self.CONTEXT)
                    create_alarm(self._ALARM, cl,)

                elif b"POST /api/alarms/" in request and b"/delete" in request:
                    logger.info("Serving: POST api/alarms/<id>/delete", self.CONTEXT)
                    path_line = request.split(b"\r\n")[0]
                    path = path_line.split(b" ")[1]
                    alarm_id = path.split(b"/")[3].decode()

                    delete_alarm(self._ALARM, cl, alarm_id)
                
                elif b"POST /api/alarms/" in request and b"/update" in request:
                    logger.info("Serving: POST api/alarms/<id>/update", self.CONTEXT)
                    path_line = request.split(b"\r\n")[0]
                    path = path_line.split(b" ")[1]
                    alarm_id = path.split(b"/")[3].decode()
                    body = request.split(b"\r\n\r\n", 1)[1]
                    data = ujson.loads(body.decode())

                    param = data.get("param")
                    value = data.get("value")

                    update_alarm_param(self._ALARM, cl, alarm_id, param, value)

                elif b"GET /api/alarms/" in request:
                    logger.info("Serving: GET api/alarms/<id>", self.CONTEXT)
                    path_line = request.split(b"\r\n")[0]
                    alarm_id = path_line.split(b"/alarms/")[1].split(b" ")[0].decode()
                    get_alarm_page(self._ALARM, cl, alarm_id)
                
                elif b"GET /api/alarms" in request:
                    logger.info("Serving: GET api/alarms", self.CONTEXT)
                    get_alarms(self._ALARM, cl)

                elif b"POST /api/timer/update" in request:
                    logger.info("Serving: POST api/timer/update", self.CONTEXT)
                    path_line = request.split(b"\r\n")[0]
                    body = request.split(b"\r\n\r\n", 1)[1]
                    data = ujson.loads(body.decode())

                    param = data.get("param")
                    value = data.get("value")
                    
                    update_timer_param(self._TIMER, cl, param, value)

                elif b"GET /api/timer" in request:
                    logger.info("Serving: GET api/timer", self.CONTEXT)
                    get_timer(self._TIMER, cl)

                elif b"POST /api/settings/update" in request:
                    logger.info("Serving: POST api/settings/update", self.CONTEXT)
                    path_line = request.split(b"\r\n")[0]
                    body = request.split(b"\r\n\r\n", 1)[1]
                    data = ujson.loads(body.decode())

                    param = data.get("param")
                    value = data.get("value")

                    update_config_param(self._CONFIG, cl, param, value)

                elif b"GET /api/settings/timezones" in request:
                    logger.info("Serving: GET api/settings/timezones", self.CONTEXT)
                    get_timezone_list(cl)

                elif b"GET /api/settings" in request:
                    logger.info("Serving: GET api/settings", self.CONTEXT)
                    get_config(self._CONFIG, cl)

                elif b"GET /api/log" in request:
                    logger.info("Serving: GET api/log", self.CONTEXT)
                    get_log(cl)

                else:
                    try:
                        first_line = request.split(b"\r\n", 1)[0]
                        parts = first_line.split(b" ")
                        path = parts[1].decode()
                    except:
                        path = "/"
                    logger.info(f"Serving static: {path}", self.CONTEXT)
                    self._serve_static(cl, path)

            except OSError as e:
                if e.args[0] != 110:
                    logger.error(f"Socket error: {e}", self.CONTEXT)
            except Exception as e:
                logger.error(f"Request error: {e}", self.CONTEXT)
            finally:
                if cl:
                    try:
                        cl.close()
                    except Exception as e:
                        logger.error(f"Error closing socket: {e}", self.CONTEXT)
                request = None
                cl = None
                gc.collect()
            await asyncio.sleep_ms(0)

        if self._server_socket:
            try:
                self._server_socket.close()
            except:
                pass
            self._server_socket = None
            logger.info("Web server stopped", self.CONTEXT)
        self._WIFI.disconnect()
        self._DISPLAY_CONTEXT.update_web_service(self.WEB_SERVICE_OFF, "")


    def http_response(self, cl, body, code=200):
        cl.send(f"HTTP/1.1 {code} OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(body)
        cl.close()

    def _serve_static(self, cl, path):
        if path.startswith("/"):
            path = path[1:]
        paths = ["icon-256.png", "manifest.json", "favicon.ico"]

        if path.startswith("assets/"):
            pass
        elif path in paths:
            pass
        else:
            path = "index.html"

        if path.endswith(".html"):
            mime = "text/html"
        elif path.endswith(".js"):
            mime = "application/javascript"
        elif path.endswith(".css"):
            mime = "text/css"
        elif path.endswith(".json"):
            mime = "application/json"
        elif path.endswith(".png"):
            mime = "image/png"
        elif path.endswith(".jpg") or path.endswith(".jpeg"):
            mime = "image/jpeg"
        else:
            mime = "application/octet-stream"

        try:
            cl.send("HTTP/1.1 200 OK\r\n")
            cl.send("Content-Type: {}\r\n".format(mime))
            cl.send("Connection: close\r\n\r\n")
            with open(f"/lib/web/{path}", "rb") as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    cl.write(chunk)

        except Exception as e:
            print("Static file error:", e)
        finally:
            try: cl.close()
            except: pass
