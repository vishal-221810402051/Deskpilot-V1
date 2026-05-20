import subprocess
import webbrowser
from urllib.parse import quote

from core.file_search import FileSearchEngine
from core.powerpoint_controller import PowerPointController
from core.window_context import WindowContext


class SafeExecutor:
    """
    Executes only whitelisted safe commands.
    """

    def __init__(self):
        self.file_search = FileSearchEngine()
        self.powerpoint = PowerPointController()
        self.window_context = WindowContext()

        self.allowed_apps = {
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],

            "vscode": [
                r"C:\Users\visha\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            ],

            "word": [
                r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
                "start winword",
            ],

            "powerpoint": [
                r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
                "start powerpnt",
            ],

            "excel": [
                r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
                "start excel",
            ],

            "outlook": [
                r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE",
                "start outlook",
            ],

            "teams": [
                "start ms-teams:",
            ],

            "notepad": [
                "notepad",
            ],

            "calculator": [
                "calc",
            ],

            "explorer": [
                "explorer",
            ],

            "settings": [
                "start ms-settings:",
            ],
        }

        self.confirmation_required = {
            "delete_file",
            "move_file",
            "rename_file",
            "send_email",
            "run_terminal",
            "shutdown",
            "restart",
        }

    def execute(self, intent: dict) -> dict:
        action = intent.get("action")

        try:
            if action in self.confirmation_required:
                approved = self._request_confirmation(intent)

                if not approved:
                    return {
                        "status": "cancelled",
                        "message": "User cancelled the action",
                    }

            if action == "open_folder":
                return self._open_folder(intent)

            if action == "open_file":
                return self._open_file(intent)

            if action == "open_app":
                return self._open_app(intent)

            if action == "search_google":
                return self._search_google(intent)

            if action == "ppt_next_slide":
                return self.powerpoint.next_slide()

            if action == "ppt_previous_slide":
                return self.powerpoint.previous_slide()

            if action == "ppt_go_to_slide":
                slide_number = int(intent.get("target"))
                return self.powerpoint.go_to_slide(slide_number)

            if action == "ppt_first_slide":
                return self.powerpoint.go_to_first_slide()

            if action == "ppt_last_slide":
                return self.powerpoint.go_to_last_slide()

            if action == "ppt_start_slideshow":
                return self.powerpoint.start_slideshow()

            if action == "ppt_end_slideshow":
                return self.powerpoint.end_slideshow()

            if action == "window_bring_front":
                return self.window_context.bring_window_front(intent.get("target"))

            if action == "window_maximize":
                return self.window_context.maximize_window(intent.get("target"))

            if action == "window_minimize":
                return self.window_context.minimize_window(intent.get("target"))

            if action == "window_restore":
                return self.window_context.restore_window(intent.get("target"))

            if action == "window_maximize_active":
                return self.window_context.maximize_active_window()

            if action == "window_minimize_active":
                return self.window_context.minimize_active_window()

            return {
                "status": "error",
                "message": f"Unsupported action: {action}",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _request_confirmation(self, intent: dict) -> bool:
        action = intent.get("action")
        target = intent.get("target")

        print("\n" + "-" * 70)
        print("Confirmation Required")
        print(f"Action : {action}")
        print(f"Target : {target}")

        response = input("Confirm action? (y/n): ").strip().lower()

        print("-" * 70)

        return response == "y"

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

        app_commands = self.allowed_apps.get(target)

        if not app_commands:
            return {
                "status": "error",
                "message": f"App not allowed: {target}",
            }

        last_error = None

        for command in app_commands:
            try:
                subprocess.Popen(command, shell=True)
                return {
                    "status": "success",
                    "message": f"Launched app: {target}",
                }

            except Exception as error:
                last_error = error

        return {
            "status": "error",
            "message": f"Failed to launch {target}: {last_error}",
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
