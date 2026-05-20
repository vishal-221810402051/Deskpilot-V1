import json
from datetime import datetime
from pathlib import Path


class CommandLogger:
    """
    Stores DeskPilot command history as JSON Lines.
    """

    def __init__(self, log_path: str = "data/command_log.jsonl"):
        self.log_file = Path(log_path)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_command(
        self,
        command_number: int,
        raw_text: str,
        corrected_text: str,
        intent: dict,
        result: dict,
    ) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "command_number": command_number,
            "raw_text": raw_text,
            "corrected_text": corrected_text,
            "intent": intent,
            "result": result,
        }

        with self.log_file.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(entry, ensure_ascii=False) + "\n"
            )
