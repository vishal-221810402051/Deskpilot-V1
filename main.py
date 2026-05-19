import threading

import keyboard

from core.listener import record_audio
from core.transcriber import SpeechTranscriber
from core.parser import CommandParser
from core.executor import SafeExecutor
from core.logger import CommandLogger


HOTKEY = "ctrl+space"


class DeskPilotApp:
    def __init__(self):
        self.transcriber = SpeechTranscriber(model_size="base")
        self.parser = CommandParser()
        self.executor = SafeExecutor()
        self.logger = CommandLogger()

        self.command_count = 0
        self.is_processing = False

    def handle_command(self):
        if self.is_processing:
            print("DeskPilot is already processing a command. Please wait.")
            return

        self.is_processing = True
        self.command_count += 1

        raw_text = ""
        intent = {}
        result = {}

        try:
            print("\n" + "=" * 70)
            print(f"Command #{self.command_count}")
            print("Listening...")

            audio_path = record_audio()

            print("Transcribing...")
            raw_text = self.transcriber.transcribe_audio(audio_path)

            print("Parsing command...")
            intent = self.parser.parse(raw_text)

            print("Executing...")
            result = self.executor.execute(intent)

            self.logger.log_command(
                command_number=self.command_count,
                raw_text=raw_text,
                intent=intent,
                result=result,
            )

            print("-" * 70)
            print(f"Voice text : {raw_text}")
            print(f"Intent     : {intent}")
            print(f"Result     : {result}")
            print("Log        : saved")
            print("-" * 70)
            print("Ready for next command.")

        except Exception as error:
            result = {
                "status": "error",
                "message": str(error),
            }

            self.logger.log_command(
                command_number=self.command_count,
                raw_text=raw_text,
                intent=intent,
                result=result,
            )

            print("-" * 70)
            print(f"DeskPilot error: {error}")
            print("Log        : saved")
            print("-" * 70)

        finally:
            self.is_processing = False


def main():
    print("DeskPilot V1 - Phase 8 Confirmation Layer")
    print("Loading assistant...")

    app = DeskPilotApp()

    print(f"Press {HOTKEY.upper()} to give a command.")
    print("Press ESC to exit.")
    print("Ready.")

    keyboard.add_hotkey(
        HOTKEY,
        lambda: threading.Thread(
            target=app.handle_command,
            daemon=True,
        ).start()
    )

    keyboard.wait("esc")
    print("DeskPilot stopped.")


if __name__ == "__main__":
    main()
