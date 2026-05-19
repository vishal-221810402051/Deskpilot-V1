import keyboard

from core.listener import record_audio
from core.transcriber import SpeechTranscriber
from core.parser import CommandParser
from core.executor import SafeExecutor


HOTKEY = "ctrl+space"


def handle_command(
    transcriber: SpeechTranscriber,
    parser: CommandParser,
    executor: SafeExecutor
):
    audio_path = record_audio()

    text = transcriber.transcribe_audio(audio_path)

    intent = parser.parse(text)

    result = executor.execute(intent)

    print("-" * 60)
    print(f"Final command text: {text}")
    print(f"Parsed intent: {intent}")
    print(f"Execution result: {result}")
    print("-" * 60)


def main():
    print("DeskPilot V1 - Phase 4 Safe Executor")

    transcriber = SpeechTranscriber(model_size="base")
    parser = CommandParser()
    executor = SafeExecutor()

    print(f"Press {HOTKEY.upper()} to execute voice commands.")
    print("Press ESC to exit.")

    keyboard.add_hotkey(
        HOTKEY,
        lambda: handle_command(
            transcriber,
            parser,
            executor
        )
    )

    keyboard.wait("esc")

    print("DeskPilot stopped.")


if __name__ == "__main__":
    main()
