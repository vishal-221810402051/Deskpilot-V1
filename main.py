import threading

import keyboard

from core.listener import record_audio
from core.transcriber import SpeechTranscriber
from core.parser import CommandParser
from core.executor import SafeExecutor


HOTKEY = "ctrl+space"


class DeskPilotApp:
    def __init__(self):
        self.transcriber = SpeechTranscriber(model_size="base")
        self.parser = CommandParser()
        self.executor = SafeExecutor()
        self.command_count = 0
        self.is_processing = False

    def handle_command(self):
        if self.is_processing:
            print("DeskPilot is already processing a command. Please wait.")
            return

        self.is_processing = True
        self.command_count += 1

        try:
            print("\n" + "=" * 70)
            print(f"Command #{self.command_count}")
            print("Listening...")

            audio_path = record_audio()

            print("Transcribing...")
            text = self.transcriber.transcribe_audio(audio_path)

            print("Parsing command...")
            intent = self.parser.parse(text)

            print("Executing...")
            result = self.executor.execute(intent)

            print("-" * 70)
            print(f"Voice text : {text}")
            print(f"Intent     : {intent}")
            print(f"Result     : {result}")
            print("-" * 70)
            print("Ready for next command.")

        except Exception as error:
            print("-" * 70)
            print(f"DeskPilot error: {error}")
            print("-" * 70)

        finally:
            self.is_processing = False


def main():
    print("DeskPilot V1 - Phase 6 Full Command Loop")
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
