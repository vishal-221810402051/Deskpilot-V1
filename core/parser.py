from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class CommandIntent:
    action: str
    target: Optional[str] = None
    location: Optional[str] = None
    raw_text: str = ""
    confidence: float = 0.0


class CommandParser:
    """
    Converts transcribed text into structured command intent.
    Phase 3 supports basic open-folder/open-file/open-app/search commands.
    """

    def parse(self, text: str) -> dict:
        clean_text = self._normalize(text)

        if not clean_text:
            return asdict(CommandIntent(
                action="unknown",
                raw_text=text,
                confidence=0.0
            ))

        if self._is_open_app_command(clean_text):
            return asdict(self._parse_open_app(clean_text, text))

        if self._is_open_file_command(clean_text):
            return self._parse_open_file(clean_text, text)

        if self._is_open_folder_command(clean_text):
            return asdict(self._parse_open_folder(clean_text, text))

        if self._is_search_google_command(clean_text):
            return asdict(self._parse_search_google(clean_text, text))

        if self._is_powerpoint_control_command(clean_text):
            return asdict(self._parse_powerpoint_control(clean_text, text))

        return asdict(CommandIntent(
            action="unknown",
            raw_text=text,
            confidence=0.0
        ))

    def _normalize(self, text: str) -> str:
        replacements = {
            " and desktop": " on desktop",
            " in desktop": " on desktop",
            " inside desktop": " on desktop",
            "folder and": "folder on",
            "file and": "file on",
            "open ballpoint": "open powerpoint",
            "open power point": "open powerpoint",
            "open hard look": "open outlook",
            "open out look": "open outlook",
            "open world": "open word",
            "slatial": "slide show",
            "slatiel": "slide show",
            "slade show": "slide show",
            "slatual": "slide show",
            "slide sho": "slide show",
            "slide showw": "slide show",
            "slideshow": "slide show",
            "the ": "",
        }

        clean = text.lower().strip()

        for char in [".", ",", "!", "?", ";", ":"]:
            clean = clean.replace(char, "")

        for wrong, correct in replacements.items():
            clean = clean.replace(wrong, correct)

        clean = " ".join(clean.split())
        return clean

    def _is_open_folder_command(self, text: str) -> bool:
        return "open" in text and "folder" in text

    def _is_open_file_command(self, text: str) -> bool:
        return "open" in text and "file" in text

    def _is_open_app_command(self, text: str) -> bool:
        app_words = [
            "chrome",
            "vscode",
            "vs code",
            "visual studio code",
            "notepad",
            "calculator",
            "word",
            "microsoft word",
            "powerpoint",
            "power point",
            "microsoft powerpoint",
            "excel",
            "microsoft excel",
            "outlook",
            "microsoft outlook",
            "teams",
            "microsoft teams",
            "file explorer",
            "explorer",
            "settings",
        ]
        return text.startswith("open") and any(app in text for app in app_words)

    def _is_search_google_command(self, text: str) -> bool:
        return text.startswith("search google for") or text.startswith("google search for")

    def _is_powerpoint_control_command(self, text: str) -> bool:
        keywords = [
            "present",
            "stop present",
            "close slide show",
            "close slate show",
            "end slide show",
            "and slide show",
            "slide show",
            "slate show",
            "slag shell",
            "slide ",
            "next slide",
            "previous slide",
            "back slide",
            "go to slide",
            "go slide",
            "first slide",
            "last slide",
            "start slideshow",
            "start slide show",
            "end slideshow",
            "end slide show",
            "stop slideshow",
            "stop slide show",
        ]

        return any(keyword in text for keyword in keywords)

    def _parse_open_folder(self, clean_text: str, raw_text: str) -> CommandIntent:
        target = clean_text

        target = target.replace("open", "")
        target = target.replace("folder", "")
        target = target.replace("on desktop", "")
        target = target.replace("inside", "")
        target = target.replace("called", "")
        target = target.strip()

        location = "desktop" if "desktop" in clean_text else None

        return CommandIntent(
            action="open_folder",
            target=target,
            location=location,
            raw_text=raw_text,
            confidence=0.85
        )

    def _parse_open_file(self, clean_text: str, raw_text: str) -> dict:
        working_text = clean_text

        location = "desktop" if "desktop" in working_text else None
        folder_name = None

        working_text = working_text.replace("open", "")
        working_text = working_text.replace("file", "")
        working_text = working_text.replace("on desktop", "")
        working_text = working_text.strip()

        if "inside folder" in working_text:
            parts = working_text.split("inside folder", 1)
            target = parts[0].strip()
            folder_name = parts[1].strip()
        elif "in folder" in working_text:
            parts = working_text.split("in folder", 1)
            target = parts[0].strip()
            folder_name = parts[1].strip()
        else:
            target = working_text

        intent = CommandIntent(
            action="open_file",
            target=target,
            location=location,
            raw_text=raw_text,
            confidence=0.75
        )

        result = asdict(intent)
        result["folder_name"] = folder_name

        return result

    def _parse_open_app(self, clean_text: str, raw_text: str) -> CommandIntent:
        target = clean_text.replace("open", "").strip()

        aliases = {
            "vs code": "vscode",
            "visual studio code": "vscode",
            "google chrome": "chrome",
            "microsoft word": "word",
            "microsoft powerpoint": "powerpoint",
            "power point": "powerpoint",
            "microsoft excel": "excel",
            "microsoft outlook": "outlook",
            "microsoft teams": "teams",
            "file explorer": "explorer",
        }

        target = aliases.get(target, target)

        return CommandIntent(
            action="open_app",
            target=target,
            location=None,
            raw_text=raw_text,
            confidence=0.85
        )

    def _parse_search_google(self, clean_text: str, raw_text: str) -> CommandIntent:
        target = clean_text
        target = target.replace("search google for", "")
        target = target.replace("google search for", "")
        target = target.strip()

        return CommandIntent(
            action="search_google",
            target=target,
            location=None,
            raw_text=raw_text,
            confidence=0.85
        )

    def _parse_powerpoint_control(self, clean_text: str, raw_text: str) -> CommandIntent:
        if clean_text in ["present", "start presentation", "start present"]:
            return CommandIntent(
                action="ppt_start_slideshow",
                raw_text=raw_text,
                confidence=0.9,
            )

        if clean_text in [
            "stop present",
            "stop presentation",
            "close slide show",
            "close slate show",
            "end slide show",
            "and slide show",
        ]:
            return CommandIntent(
                action="ppt_end_slideshow",
                raw_text=raw_text,
                confidence=0.9,
            )

        if clean_text.startswith("slide "):
            slide_number = self._extract_number(clean_text)

            if slide_number is not None:
                return CommandIntent(
                    action="ppt_go_to_slide",
                    target=str(slide_number),
                    raw_text=raw_text,
                    confidence=0.9,
                )

        if "next slide" in clean_text:
            return CommandIntent(
                action="ppt_next_slide",
                raw_text=raw_text,
                confidence=0.9,
            )

        if "previous slide" in clean_text or "back slide" in clean_text:
            return CommandIntent(
                action="ppt_previous_slide",
                raw_text=raw_text,
                confidence=0.9,
            )

        if "first slide" in clean_text:
            return CommandIntent(
                action="ppt_first_slide",
                raw_text=raw_text,
                confidence=0.9,
            )

        if "last slide" in clean_text:
            return CommandIntent(
                action="ppt_last_slide",
                raw_text=raw_text,
                confidence=0.9,
            )

        if "start slide show" in clean_text:
            return CommandIntent(
                action="ppt_start_slideshow",
                raw_text=raw_text,
                confidence=0.9,
            )

        if (
            "end slideshow" in clean_text
            or "end slide show" in clean_text
            or "stop slideshow" in clean_text
            or "stop slide show" in clean_text
        ):
            return CommandIntent(
                action="ppt_end_slideshow",
                raw_text=raw_text,
                confidence=0.9,
            )

        if "go to slide" in clean_text or "go slide" in clean_text:
            slide_number = self._extract_number(clean_text)

            if slide_number is not None:
                return CommandIntent(
                    action="ppt_go_to_slide",
                    target=str(slide_number),
                    raw_text=raw_text,
                    confidence=0.9,
                )

        return CommandIntent(
            action="unknown",
            raw_text=raw_text,
            confidence=0.0,
        )

    def _extract_number(self, text: str) -> int | None:
        number_words = {
            "one": 1,
            "first": 1,
            "two": 2,
            "second": 2,
            "three": 3,
            "third": 3,
            "four": 4,
            "fourth": 4,
            "five": 5,
            "fifth": 5,
            "six": 6,
            "sixth": 6,
            "seven": 7,
            "seventh": 7,
            "eight": 8,
            "eighth": 8,
            "nine": 9,
            "ninth": 9,
            "ten": 10,
            "tenth": 10,
        }

        for token in text.split():
            if token.isdigit():
                return int(token)

            if token in number_words:
                return number_words[token]

        return None
