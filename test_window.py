from pprint import pprint

from core.window_context import WindowContext

ctx = WindowContext()

desktop = ctx.get_desktop_context()

print("\nFOREGROUND WINDOW")
pprint(desktop["foreground"])

print("\nVISIBLE WINDOWS")
for window in desktop["windows"]:
    print(
        f"{window['app_name']:15} | "
        f"{window['state']:10} | "
        f"{window['title']}"
    )
