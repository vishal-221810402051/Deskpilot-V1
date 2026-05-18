import keyboard
from core.listener import record_audio


HOTKEY = "ctrl+space"


def main():
    print("DeskPilot V1 - Phase 1 Audio Capture")
    print(f"Press {HOTKEY.upper()} to record a 5-second command.")
    print("Press ESC to exit.")

    keyboard.add_hotkey(HOTKEY, lambda: record_audio())

    keyboard.wait("esc")
    print("DeskPilot stopped.")


if __name__ == "__main__":
    main()
