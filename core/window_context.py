import psutil
import win32gui
import win32process
import win32con


class WindowContext:
    """
    Detects active window and all visible desktop windows.
    """

    def get_active_window_info(self) -> dict:
        try:
            hwnd = win32gui.GetForegroundWindow()
            return self._build_window_info(hwnd, is_foreground=True)

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }

    def list_windows(self) -> list[dict]:
        windows = []

        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return

            title = win32gui.GetWindowText(hwnd).strip()

            if not title:
                return

            info = self._build_window_info(hwnd)

            if info.get("status") == "success":
                windows.append(info)

        win32gui.EnumWindows(callback, None)

        return windows

    def get_desktop_context(self) -> dict:
        return {
            "status": "success",
            "foreground": self.get_active_window_info(),
            "windows": self.list_windows(),
        }

    def _build_window_info(self, hwnd: int, is_foreground: bool = False) -> dict:
        try:
            if not hwnd:
                return {
                    "status": "error",
                    "message": "Invalid window handle",
                }

            title = win32gui.GetWindowText(hwnd).strip()

            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(process_id)

            process_name = process.name()
            app_name = self._normalize_app_name(process_name)

            placement = win32gui.GetWindowPlacement(hwnd)
            show_cmd = placement[1]

            if show_cmd == win32con.SW_SHOWMINIMIZED:
                state = "minimized"
            elif show_cmd == win32con.SW_SHOWMAXIMIZED:
                state = "maximized"
            else:
                state = "normal"

            rect = win32gui.GetWindowRect(hwnd)

            return {
                "status": "success",
                "hwnd": hwnd,
                "title": title,
                "process_id": process_id,
                "process_name": process_name,
                "app_name": app_name,
                "state": state,
                "rect": {
                    "left": rect[0],
                    "top": rect[1],
                    "right": rect[2],
                    "bottom": rect[3],
                },
                "is_foreground": is_foreground,
            }

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }

    def _normalize_app_name(self, process_name: str) -> str:
        name = process_name.lower()

        app_map = {
            "powerpnt.exe": "powerpoint",
            "winword.exe": "word",
            "excel.exe": "excel",
            "outlook.exe": "outlook",
            "chrome.exe": "chrome",
            "msedge.exe": "edge",
            "code.exe": "vscode",
            "explorer.exe": "file_explorer",
            "cmd.exe": "terminal",
            "powershell.exe": "powershell",
            "windowsterminal.exe": "terminal",
            "applicationframehost.exe": "windows_app",
        }

        return app_map.get(name, name.replace(".exe", ""))
