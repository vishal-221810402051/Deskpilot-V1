import keyboard

from core.listener import record_audio
from core.transcriber import SpeechTranscriber
from core.parser import CommandParser


HOTKEY = "ctrl+space"


def handle_command(transcriber: SpeechTranscriber, parser: CommandParser):
    audio_path = record_audio()
    text = transcriber.transcribe_audio(audio_path)
    intent = parser.parse(text)

    print("-" * 50)
    print(f"Final command text: {text}")
    print(f"Parsed intent: {intent}")
    print("-" * 50)


def main():
    print("DeskPilot V1 - Phase 3 Command Parser")
    print("Loading speech model. First launch may take time...")

    transcriber = SpeechTranscriber(model_size="base")
    parser = CommandParser()

    print(f"Press {HOTKEY.upper()} to record, transcribe, and parse.")
    print("Press ESC to exit.")

    keyboard.add_hotkey(HOTKEY, lambda: handle_command(transcriber, parser))

    keyboard.wait("esc")
    print("DeskPilot stopped.")


if __name__ == "__main__":
    main()
