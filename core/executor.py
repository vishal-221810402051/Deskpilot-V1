import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote


class SafeExecutor:
    """
    Executes only whitelisted safe commands.
    """

    def __init__(self):
        self.allowed_apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "vscode": r"C:\Users\visha\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
        }

    def execute(self, intent: dict) -> dict:
        action = intent.get("action")

        try:
            if action == "open_folder":
                return self._open_folder(intent)

            if action == "open_app":
                return self._open_app(intent)

            if action == "search_google":
                return self._search_google(intent)

            return {
                "status": "error",
                "message": f"Unsupported action: {action}"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def _open_folder(self, intent: dict) -> dict:
        target = intent.get("target", "").strip().lower()
        location = intent.get("location")

        if location == "desktop":
            base_path = Path.home() / "Desktop"
        else:
            base_path = Path.home()

        folder_path = base_path / target

        if not folder_path.exists():
            return {
                "status": "error",
                "message": f"Folder not found: {folder_path}"
            }

        subprocess.Popen(f'explorer "{folder_path}"')

        return {
            "status": "success",
            "message": f"Opened folder: {folder_path}"
        }

    def _open_app(self, intent: dict) -> dict:
        target = intent.get("target", "").strip().lower()

        app_path = self.allowed_apps.get(target)

        if not app_path:
            return {
                "status": "error",
                "message": f"App not allowed: {target}"
            }

        subprocess.Popen(app_path)

        return {
            "status": "success",
            "message": f"Launched app: {target}"
        }

    def _search_google(self, intent: dict) -> dict:
        query = intent.get("target", "").strip()

        if not query:
            return {
                "status": "error",
                "message": "Empty Google search query"
            }

        encoded_query = quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"

        webbrowser.open(url)

        return {
            "status": "success",
            "message": f"Searched Google for: {query}"
        }
