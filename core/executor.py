import subprocess
import webbrowser
from urllib.parse import quote

from core.file_search import FileSearchEngine


class SafeExecutor:
    """
    Executes only whitelisted safe commands.
    """

    def __init__(self):
        self.file_search = FileSearchEngine()

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

            if action == "open_file":
                return self._open_file(intent)

            if action == "open_app":
                return self._open_app(intent)

            if action == "search_google":
                return self._search_google(intent)

            return {
                "status": "error",
                "message": f"Unsupported action: {action}",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _open_folder(self, intent: dict) -> dict:
        target = intent.get("target", "").strip().lower()
        location = intent.get("location")

        folder_path = self.file_search.find_folder(target, location)

        if not folder_path:
            return {
                "status": "error",
                "message": f"Folder not found: {target}",
            }

        subprocess.Popen(f'explorer "{folder_path}"')

        return {
            "status": "success",
            "message": f"Opened folder: {folder_path}",
        }

    def _open_file(self, intent: dict) -> dict:
        target = intent.get("target", "").strip().lower()
        location = intent.get("location")
        folder_name = intent.get("folder_name")

        file_path = self.file_search.find_file(
            file_name=target,
            folder_name=folder_name,
            location=location,
        )

        if not file_path:
            return {
                "status": "error",
                "message": f"File not found: {target}",
            }

        subprocess.Popen(f'explorer "{file_path}"')

        return {
            "status": "success",
            "message": f"Opened file: {file_path}",
        }

    def _open_app(self, intent: dict) -> dict:
        target = intent.get("target", "").strip().lower()

        app_path = self.allowed_apps.get(target)

        if not app_path:
            return {
                "status": "error",
                "message": f"App not allowed: {target}",
            }

        subprocess.Popen(app_path)

        return {
            "status": "success",
            "message": f"Launched app: {target}",
        }

    def _search_google(self, intent: dict) -> dict:
        query = intent.get("target", "").strip()

        if not query:
            return {
                "status": "error",
                "message": "Empty Google search query",
            }

        encoded_query = quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"

        webbrowser.open(url)

        return {
            "status": "success",
            "message": f"Searched Google for: {query}",
        }
