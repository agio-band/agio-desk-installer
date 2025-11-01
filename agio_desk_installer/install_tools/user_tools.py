import json
import os
import sys
import platform
import shutil
from pathlib import Path
import logging

from agio.tools import app_dirs
logger = logging.getLogger(__name__)

try:
    import win32com.client
except ImportError:
    win32com = None


# Paths
def get_desktop_path() -> Path:
    system = platform.system()
    if system == "Windows":
        from win32com.shell import shell, shellcon
        return Path(shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0))
    elif system == "Linux":
        xdg_path = Path.home() / "Desktop"
        return xdg_path if xdg_path.exists() else Path.home()
    elif system == "Darwin":  # macOS
        return Path.home() / "Desktop"
    else:
        raise OSError(f"Unsupported system: {system}")


def get_main_menu_path() -> Path:
    system = platform.system()
    if system == "Windows":
        from win32com.shell import shell, shellcon
        return Path(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, 0, 0))
    elif system == "Linux":
        path = Path.home() / ".local/share/applications"
        path.mkdir(parents=True, exist_ok=True)
        return path
    elif system == "Darwin":
        return Path("/Applications")
    else:
        raise OSError(f"Unsupported system: {system}")


# create shortcuts
def create_desktop_shortcut(shortcut_name, executable_file, icon=None, workdir=None, args: list[str] = None):
    system = platform.system()
    desktop_path = get_desktop_path()
    if system == "Windows":
        create_windows_shortcut(desktop_path, shortcut_name, executable_file, icon, workdir, args)
    elif system == "Linux":
        create_linux_shortcut(desktop_path, shortcut_name, executable_file, icon, workdir, args)
    elif system == "Darwin":
        create_macos_shortcut(desktop_path, shortcut_name, executable_file, icon, workdir, args)
    else:
        raise OSError("Unsupported OS")


def create_main_menu_shortcut(shortcut_name, executable_file, icon=None, workdir=None, args: list[str] = None):
    system = platform.system()
    menu_path = get_main_menu_path()
    if system == "Windows":
        create_windows_shortcut(menu_path, shortcut_name, executable_file, icon, workdir, args)
    elif system == "Linux":
        create_linux_shortcut(menu_path, shortcut_name, executable_file, icon, workdir, args)
    elif system == "Darwin":
        create_macos_shortcut(menu_path, shortcut_name, executable_file, icon, workdir, args)
    else:
        raise OSError("Unsupported OS")


# windows
def create_windows_shortcut(
        folder, shortcut_name, executable, icon=None, workdir=None, args: list[str] = None, replace=True
):
    if win32com is None:
        raise ImportError("pywin32 is required on Windows")

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    shortcut_path = folder / f"{shortcut_name}.lnk"

    if shortcut_path.exists() and not replace:
        return shortcut_path

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(executable)
    if args:
        shortcut.Arguments = " ".join(args)
    shortcut.WorkingDirectory = str(workdir or Path(executable).parent)
    if icon:
        shortcut.IconLocation = str(icon)
    shortcut.save()
    return shortcut_path


# linux
def create_linux_shortcut(
        folder, shortcut_name, executable, icon=None, workdir=None, args: list[str] = None, replace=True
):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    shortcut_path = folder / f"{shortcut_name}.desktop"

    if shortcut_path.exists() and not replace:
        return shortcut_path

    cmd = " ".join([str(executable)] + (args or []))
    content = f"""[Desktop Entry]
Type=Application
Name={shortcut_name}
Exec={cmd}
Icon={icon or ""}
Path={workdir or Path(executable).parent}
Terminal=false
Categories=Utility;
"""
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write(content)

    os.chmod(shortcut_path, 0o755)
    return shortcut_path


# macos
def create_macos_shortcut(
        folder, shortcut_name, executable, icon=None, workdir=None, args: list[str] = None, replace=True
):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    shortcut_path = folder / f"{shortcut_name}.app"

    if shortcut_path.exists() and not replace:
        return shortcut_path

    applescript = f"""
    tell application "Terminal"
        do script "{executable} {' '.join(args or [])}"
    end tell
    """

    tmp_script = folder / f"{shortcut_name}.applescript"
    with open(tmp_script, "w", encoding="utf-8") as f:
        f.write(applescript)

    os.system(f"osacompile -o '{shortcut_path}' '{tmp_script}'")
    tmp_script.unlink(missing_ok=True)
    return shortcut_path


# cleanup
def delete_shortcuts(shortcut_name):
    system = platform.system()
    exts = {
        "Windows": ".lnk",
        "Linux": ".desktop",
        "Darwin": ".app",
    }
    ext = exts.get(system)
    if not ext:
        raise OSError("Unsupported OS")

    for base_path in (get_desktop_path(), get_main_menu_path()):
        for file in base_path.glob(f"{shortcut_name}{ext}"):
            try:
                if file.is_dir():
                    shutil.rmtree(file)
                else:
                    file.unlink()
            except Exception as e:
                print(f"Cannot remove {file}: {e}")
    return True


if __name__ == "__main__":
    create_desktop_shortcut("MyApp", sys.executable , icon=None)
    create_main_menu_shortcut("MyApp", sys.executable , icon=None)
    delete_shortcuts("MyApp")


def save_info_file(data: dict):
    install_info_file = app_dirs.config_dir('agio-desk.json')
    install_info_file.parent.mkdir(parents=True, exist_ok=True)
    with open(install_info_file, 'w') as f:
        json.dump(data, f)


def load_info_file():
    install_info_file = app_dirs.config_dir('agio-desk.json')
    if not install_info_file.exists():
        return {}
    try:
        with open(install_info_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.error('Failed read info file', e)
        return {}
    return data


def delete_info_file():
    file = app_dirs.config_dir('agio-desk.json')
    if file.exists():
        file.unlink()
