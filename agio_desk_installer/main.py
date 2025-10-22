import argparse
import os
import sys

from agio_desk_installer.tools import checker

# path_to_config = os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Roaming\agio\settings.db") где конфиг ?
# path_to_config_linux = "~/.config/agio/settings.db"

if sys.platform.startswith("win"):
    path_to_desk = os.path.expandvars(r"%LOCALAPPDATA%\agio-desk")
if sys.platform.startswith("linux"):
    path_to_desk = os.path.expanduser("~/.local/share/agio-desk")

def main(
        path_to_install: str,
        add_shortcut: bool,
        add_shortcut_menu: bool,
        autorun: bool,
        open_docs: bool,
        open_settings: bool,
):
    # win
    if sys.platform.startswith("win"):
        print("Installing agio.desk for windows...", flush=True)

        # winfsp
        checker.winfsp_tool()

        # drive
        # path_to_drive = path_to_install + "/agio-drive/"
        # checker.drive_tool(path_to_drive, add_shortcut) ??????????

        # ffmpeg
        checker.ffmpeg_tools()

        # finalizing
        if add_shortcut:
            print(f"Adding shortcut in desktop", flush=True)
        if add_shortcut_menu:
            print(f"Adding shortcut menu in desktop", flush=True)
        if autorun:
            print(f"Autorunning desk", flush=True)
        if open_docs:
            print("Opening docs ссылка на доку ?", flush=True)
        if open_settings:
            print("Opening settings <UNK> <UNK> <UNK> ?", flush=True)

        print("Done, agio.desk installing in:", path_to_install, flush=True)

if __name__ == '__main__':
    main("C/Windows/agio.desk")
