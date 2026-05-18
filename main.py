import keyboard

from core.listener import record_audio
from core.transcriber import SpeechTranscriber


HOTKEY = "ctrl+space"


def handle_command(transcriber: SpeechTranscriber):
    audio_path = record_audio()
    text = transcriber.transcribe_audio(audio_path)

    print("-" * 50)
    print(f"Final command text: {text}")
    print("-" * 50)


def main():
    print("DeskPilot V1 - Phase 2 Speech-to-Text")
    print("Loading speech model. First launch may take time...")

    transcriber = SpeechTranscriber(model_size="base")

    print(f"Press {HOTKEY.upper()} to record and transcribe.")
    print("Press ESC to exit.")

    keyboard.add_hotkey(HOTKEY, lambda: handle_command(transcriber))

    keyboard.wait("esc")
    print("DeskPilot stopped.")


if __name__ == "__main__":
    main()
