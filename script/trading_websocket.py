# trading_websocket.py
import json
import time
import threading
import websocket
import ssl
import certifi
from logger import log_message
from config import USER_ID, PASSWORD

class TradingWebSocket:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.session_id = None
        self.responses = {}
        self.lock = threading.Lock()

    def on_open(self, ws):
        log_message("info", "WebSocket geöffnet. Sende Login...")
        login_payload = json.dumps({
            "command": "login",
            "arguments": {
                "userId": USER_ID,
                "password": PASSWORD
            }
        })
        ws.send(login_payload)

    def on_close(self, ws, code, msg):
        log_message("warning", f"Verbindung geschlossen: code={code}, msg={msg}")

    def on_message(self, ws, message):
        data = json.loads(message)
        log_message("info", f"Antwort empfangen: {data}")
        command = data.get("command", "")  # Befehl identifizieren
        with self.lock:
            # Session-ID extrahieren
            if "streamSessionId" in data:
                self.session_id = data["streamSessionId"]
            self.responses[command] = data

    def on_error(self, ws, error):
        log_message("error", f"WebSocket-Fehler: {error}")

    def send_json(self, payload):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(payload))
        else:
            log_message("error", "Kann nicht senden, WebSocket nicht verbunden.")

    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error
        )
        self.thread = threading.Thread(target=self.ws.run_forever, kwargs={
            "sslopt": {
                "cert_reqs": ssl.CERT_REQUIRED,
                "ca_certs": certifi.where()
            }
        })
        self.thread.start()
        log_message("info", f"Connecting to {self.url}")

    def disconnect(self):
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join()
        log_message("info", "Disconnecting")

    def wait_for_data(self, key, timeout=15):
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                if key in self.responses:
                    return self.responses.pop(key)
            time.sleep(0.5)
        return None

    def keep_alive(self):
        from config import PING_INTERVAL
        while True:
            if self.ws and self.ws.sock and self.ws.sock.connected:
                ping_request = {"command": "ping"}
                self.send_json(ping_request)
                log_message("info", "Ping gesendet.")
            else:
                log_message("warning", "WebSocket ist nicht verbunden.")
            time.sleep(PING_INTERVAL)
