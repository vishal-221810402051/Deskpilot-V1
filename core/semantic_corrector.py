from rapidfuzz import process, fuzz


class SemanticCorrector:
    """
    Corrects imperfect speech text into safe canonical DeskPilot commands.
    """

    def __init__(self):
        self.action_aliases = {
            "minimize": [
                "minimize", "minimum", "minimise", "make small",
                "hide", "send down", "put down"
            ],
            "maximize": [
                "maximize", "maximise", "make big", "full screen",
                "expand", "make large"
            ],
            "restore": [
                "restore", "bring back", "show again", "return"
            ],
            "bring": [
                "bring", "switch to", "focus", "go to", "open window",
                "bring front", "bring to front", "show"
            ],
            "open": [
                "open", "launch", "start"
            ],
            "search_google": [
                "search google for", "google", "search for", "look up"
            ],
            "present": [
                "present", "start presentation", "start slide show",
                "start slideshow", "begin presentation"
            ],
            "stop_present": [
                "stop present", "stop presentation", "end presentation",
                "end slideshow", "close present", "close slide show"
            ],
            "next_slide": [
                "next slide", "next", "forward slide", "move next"
            ],
            "previous_slide": [
                "previous slide", "back slide", "back", "go back"
            ],
        }

        self.app_aliases = {
            "chrome": ["chrome", "google chrome", "go and friend", "grown"],
            "powerpoint": ["powerpoint", "power point", "ballpoint", "power point"],
            "word": ["word", "microsoft word", "world"],
            "excel": ["excel", "microsoft excel", "xl"],
            "outlook": ["outlook", "microsoft outlook", "hard look", "out look"],
            "vscode": ["vscode", "vs code", "visual studio code", "code"],
            "spotify": ["spotify", "spot if i", "spotty fly", "45"],
            "file_explorer": ["file explorer", "explorer", "windows explorer"],
            "notepad": ["notepad", "note pad"],
            "calculator": ["calculator", "calc"],
            "settings": ["settings", "windows settings"],
            "teams": ["teams", "microsoft teams"],
            "chatgpt": ["chatgpt", "chat gpt", "charged gpt", "charge gpt"],
        }

    def correct(self, text: str) -> str:
        clean = self._clean(text)

        ppt_command = self._correct_powerpoint(clean)
        if ppt_command:
            return ppt_command

        search_command = self._correct_search(clean)
        if search_command:
            return search_command

        window_command = self._correct_window_action(clean)
        if window_command:
            return window_command

        open_app_command = self._correct_open_app(clean)
        if open_app_command:
            return open_app_command

        return clean

    def _clean(self, text: str) -> str:
        clean = text.lower().strip()

        for char in [".", ",", "!", "?", ";", ":"]:
            clean = clean.replace(char, "")

        clean = " ".join(clean.split())
        return clean

    def _best_action(self, text: str) -> str | None:
        choices = []

        for canonical, aliases in self.action_aliases.items():
            for alias in aliases:
                choices.append((alias, canonical))

        match = process.extractOne(
            text,
            [item[0] for item in choices],
            scorer=fuzz.WRatio,
        )

        if not match:
            return None

        alias, score, _ = match

        if score < 72:
            return None

        for original_alias, canonical in choices:
            if original_alias == alias:
                return canonical

        return None

    def _best_app(self, text: str) -> str | None:
        choices = []

        for canonical, aliases in self.app_aliases.items():
            for alias in aliases:
                choices.append((alias, canonical))

        match = process.extractOne(
            text,
            [item[0] for item in choices],
            scorer=fuzz.WRatio,
        )

        if not match:
            return None

        alias, score, _ = match

        if score < 65:
            return None

        for original_alias, canonical in choices:
            if original_alias == alias:
                return canonical

        return None

    def _correct_window_action(self, clean: str) -> str | None:
        action = self._best_action(clean)

        if action not in {"minimize", "maximize", "restore", "bring"}:
            return None

        app = self._best_app(clean)

        if not app:
            return None

        if action == "bring":
            return f"bring {app} front"

        return f"{action} {app}"

    def _correct_open_app(self, clean: str) -> str | None:
        if not any(word in clean for word in ["open", "launch", "start"]):
            return None

        app = self._best_app(clean)

        if not app:
            return None

        return f"open {app}"

    def _correct_search(self, clean: str) -> str | None:
        prefixes = [
            "search google for",
            "google search for",
            "search for",
            "look up",
        ]

        for prefix in prefixes:
            if clean.startswith(prefix):
                query = clean.replace(prefix, "", 1).strip()

                if query:
                    return f"search google for {query}"

        return None

    def _correct_powerpoint(self, clean: str) -> str | None:
        if clean in ["present", "start present", "start presentation"]:
            return "present"

        if clean in ["stop present", "close present", "stop presentation", "end presentation"]:
            return "stop present"

        if "next" in clean and "slide" in clean:
            return "next slide"

        if ("previous" in clean or "back" in clean) and "slide" in clean:
            return "previous slide"

        if "first slide" in clean:
            return "first slide"

        if "last slide" in clean:
            return "last slide"

        # handles "slide 5", "slide five", "go to slide 3"
        if "slide" in clean:
            return clean

        action = self._best_action(clean)

        if action == "present":
            return "present"

        if action == "stop_present":
            return "stop present"

        if action == "next_slide":
            return "next slide"

        if action == "previous_slide":
            return "previous slide"

        return None
