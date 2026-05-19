from pathlib import Path
from rapidfuzz import fuzz, process


class FileSearchEngine:
    """
    Fuzzy file/folder search for DeskPilot.
    """

    def __init__(self):
        self.desktop_path = Path.home() / "Desktop"

    def find_folder(self, folder_name: str, location: str | None = None) -> Path | None:
        base_path = self._get_base_path(location)

        if not base_path.exists():
            return None

        folders = [p for p in base_path.iterdir() if p.is_dir()]

        return self._best_match(folder_name, folders)

    def find_file(
        self,
        file_name: str,
        folder_name: str | None = None,
        location: str | None = None,
    ) -> Path | None:
        base_path = self._get_base_path(location)

        if folder_name:
            folder_path = self.find_folder(folder_name, location)
            if folder_path:
                base_path = folder_path

        if not base_path.exists():
            return None

        files = [p for p in base_path.rglob("*") if p.is_file()]

        return self._best_match(file_name, files)

    def _get_base_path(self, location: str | None) -> Path:
        if location == "desktop":
            return self.desktop_path

        return Path.home()

    def _best_match(self, query: str, paths: list[Path], threshold: int = 60) -> Path | None:
        if not query or not paths:
            return None

        choices = {self._clean_name(path.stem): path for path in paths}

        result = process.extractOne(
            self._clean_name(query),
            choices.keys(),
            scorer=fuzz.WRatio,
        )

        if not result:
            return None

        match_name, score, _ = result

        if score < threshold:
            return None

        return choices[match_name]

    def _clean_name(self, name: str) -> str:
        clean = name.lower()

        for char in [".", "_", "-", "(", ")", "[", "]"]:
            clean = clean.replace(char, " ")

        return " ".join(clean.split())
