import os
import threading
import time
from datetime import datetime

import keyboard

import config

from core.listener import record_audio
from core.transcriber import SpeechTranscriber
from core.parser import CommandParser
from core.executor import SafeExecutor
from core.gesture_router import GestureRouter
from core.gesture_server import GestureServer
from core.logger import CommandLogger
from core.semantic_corrector import SemanticCorrector


class DeskPilotApp:
    def __init__(self):
        self.transcriber = SpeechTranscriber(
            model_size=config.WHISPER_MODEL_SIZE
        )

        self.parser = CommandParser()
        self.executor = SafeExecutor()
        self.logger = CommandLogger()
        self.corrector = SemanticCorrector()
        self.gesture_router = GestureRouter()

        self.command_count = 0
        self.is_processing = False

    def _timestamp(self) -> str:
        if not config.ENABLE_TIMESTAMPS:
            return ""

        return datetime.now().strftime("[%H:%M:%S] ")

    def handle_command(self):
        if self.is_processing:
            print(f"{self._timestamp()}DeskPilot is busy.")
            return

        self.is_processing = True
        self.command_count += 1

        raw_text = ""
        corrected_text = ""
        intent = {}
        result = {}

        start_time = time.time()

        try:
            print("\n" + "=" * 72)

            print(
                f"{self._timestamp()}DeskPilot Command #{self.command_count}"
            )

            print(f"{self._timestamp()}Listening...")

            audio_path = record_audio(
                duration=config.RECORD_DURATION
            )

            print(f"{self._timestamp()}Transcribing...")

            raw_text = self.transcriber.transcribe_audio(audio_path)

            print(f"{self._timestamp()}Parsing command...")

            corrected_text = self.corrector.correct(raw_text)
            intent = self.parser.parse(corrected_text)

            print(f"{self._timestamp()}Executing command...")

            result = self.executor.execute(intent)

            elapsed = round(time.time() - start_time, 2)

            self.logger.log_command(
                command_number=self.command_count,
                raw_text=raw_text,
                corrected_text=corrected_text,
                intent=intent,
                result=result,
            )

            print("-" * 72)

            print(f"Voice Text     : {raw_text}")
            print(f"Corrected Text : {corrected_text}")
            print(f"Intent         : {intent}")
            print(f"Result         : {result}")
            print(f"Duration       : {elapsed}s")
            print("Log            : saved")

            print("-" * 72)

            print(f"{self._timestamp()}Ready for next command.")

        except Exception as error:
            elapsed = round(time.time() - start_time, 2)

            result = {
                "status": "error",
                "message": str(error),
            }

            self.logger.log_command(
                command_number=self.command_count,
                raw_text=raw_text,
                corrected_text=corrected_text,
                intent=intent,
                result=result,
            )

            print("-" * 72)

            print(f"DeskPilot error: {error}")
            print(f"Duration       : {elapsed}s")
            print("Log            : saved")

            print("-" * 72)

        finally:
            self.is_processing = False

    def handle_gesture(self, gesture: str):
        if self.is_processing:
            print(f"{self._timestamp()}DeskPilot is busy.")
            return

        self.is_processing = True
        self.command_count += 1

        result = {}
        intent = {}

        start_time = time.time()

        try:
            print("\n" + "=" * 72)
            print(f"{self._timestamp()}Gesture Command #{self.command_count}")
            print(f"{self._timestamp()}Gesture detected: {gesture}")

            intent = self.gesture_router.gesture_to_intent(gesture)

            print(f"{self._timestamp()}Executing gesture action...")
            result = self.executor.execute(intent)

            elapsed = round(time.time() - start_time, 2)

            self.logger.log_command(
                command_number=self.command_count,
                raw_text=f"GESTURE:{gesture}",
                corrected_text=f"GESTURE:{gesture}",
                intent=intent,
                result=result,
            )

            print("-" * 72)
            print(f"Gesture       : {gesture}")
            print(f"Intent        : {intent}")
            print(f"Result        : {result}")
            print(f"Duration      : {elapsed}s")
            print("Log           : saved")
            print("-" * 72)
            print(f"{self._timestamp()}Ready for next command.")

        except Exception as error:
            elapsed = round(time.time() - start_time, 2)

            result = {
                "status": "error",
                "message": str(error),
            }

            self.logger.log_command(
                command_number=self.command_count,
                raw_text=f"GESTURE:{gesture}",
                corrected_text=f"GESTURE:{gesture}",
                intent=intent,
                result=result,
            )

            print("-" * 72)
            print(f"DeskPilot gesture error: {error}")
            print(f"Duration              : {elapsed}s")
            print("Log                   : saved")
            print("-" * 72)

        finally:
            self.is_processing = False


def print_banner():
    print("=" * 72)
    print("DeskPilot V1 — Intelligent Hands-Free Desktop Assistant")
    print("=" * 72)


def main():
    if config.ENABLE_TERMINAL_CLEAR:
        os.system("cls")

    print_banner()

    print("[SYSTEM] Loading assistant components...")

    app = DeskPilotApp()

    gesture_server = GestureServer(app_controller=app)
    gesture_server.start_background()

    print("[SYSTEM] Assistant ready.")
    print(f"[SYSTEM] Hotkey : {config.HOTKEY.upper()}")
    print(f"[SYSTEM] Record Duration : {config.RECORD_DURATION}s")
    print("[GESTURE SERVER] HTTP receiver running on port 8765")
    print("[GESTURE SERVER] POST /gesture with {'gesture':'swipe_right_to_left'}")
    print("[GESTURE] ALT+RIGHT : swipe right-to-left / next slide")
    print("[GESTURE] ALT+LEFT  : swipe left-to-right / previous slide")
    print("[GESTURE] ALT+UP    : swipe up / present")
    print("[GESTURE] ALT+DOWN  : swipe down / stop present")
    print("[GESTURE] ALT+X     : twist clockwise / maximize active")
    print("[GESTURE] ALT+M     : twist anticlockwise / minimize active")
    print("[GESTURE] ALT+P     : double tap / bring PowerPoint front")
    print("[SYSTEM] Press ESC to exit.")

    keyboard.add_hotkey(
        config.HOTKEY,
        lambda: threading.Thread(
            target=app.handle_command,
            daemon=True,
        ).start()
    )

    keyboard.add_hotkey(
        "alt+right",
        lambda: threading.Thread(
            target=app.handle_gesture,
            args=("swipe_right_to_left",),
            daemon=True,
        ).start(),
    )

    keyboard.add_hotkey(
        "alt+left",
        lambda: threading.Thread(
            target=app.handle_gesture,
            args=("swipe_left_to_right",),
            daemon=True,
        ).start(),
    )

    keyboard.add_hotkey(
        "alt+up",
        lambda: threading.Thread(
            target=app.handle_gesture,
            args=("swipe_up",),
            daemon=True,
        ).start(),
    )

    keyboard.add_hotkey(
        "alt+down",
        lambda: threading.Thread(
            target=app.handle_gesture,
            args=("swipe_down",),
            daemon=True,
        ).start(),
    )

    keyboard.add_hotkey(
        "alt+x",
        lambda: threading.Thread(
            target=app.handle_gesture,
            args=("twist_clockwise",),
            daemon=True,
        ).start(),
    )

    keyboard.add_hotkey(
        "alt+m",
        lambda: threading.Thread(
            target=app.handle_gesture,
            args=("twist_anticlockwise",),
            daemon=True,
        ).start(),
    )

    keyboard.add_hotkey(
        "alt+p",
        lambda: threading.Thread(
            target=app.handle_gesture,
            args=("double_tap",),
            daemon=True,
        ).start(),
    )

    keyboard.wait("esc")

    print("[SYSTEM] DeskPilot stopped.")


if __name__ == "__main__":
    main()
