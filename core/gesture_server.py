import threading

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


class GesturePayload(BaseModel):
    gesture: str


class GestureServer:
    """
    Local HTTP server for receiving gesture events from future ESP32 hardware.
    """

    def __init__(self, app_controller, host: str = "0.0.0.0", port: int = 8765):
        self.app_controller = app_controller
        self.host = host
        self.port = port
        self.api = FastAPI(title="DeskPilot Gesture Server")

        self._setup_routes()

    def _setup_routes(self):
        @self.api.get("/health")
        def health():
            return {
                "status": "ok",
                "service": "DeskPilot Gesture Server",
            }

        @self.api.post("/gesture")
        def receive_gesture(payload: GesturePayload):
            gesture = payload.gesture.strip()

            threading.Thread(
                target=self.app_controller.handle_gesture,
                args=(gesture,),
                daemon=True,
            ).start()

            return {
                "status": "received",
                "gesture": gesture,
            }

    def start_background(self):
        thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        thread.start()

    def _run(self):
        uvicorn.run(
            self.api,
            host=self.host,
            port=self.port,
            log_level="warning",
        )
