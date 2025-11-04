import logging
import os
import platform
import shutil
from pathlib import Path

from agio.tools import app_dirs
from agio_desk_installer.install_tools import file_tools

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
    icon = icon or get_icon_path('ico')
    shortcut.IconLocation = str(icon)
    shortcut.save()
    # todo create for console version
    logger.info('Shortcut created: %s', shortcut_path)
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
Icon={icon or get_icon_path('png') or ""}
Path={workdir or Path(executable).parent}
Terminal=false
Categories=Utility;
"""
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write(content)
    # todo create for console version

    os.chmod(shortcut_path, 0o755)
    logger.info('Shortcut created: %s', shortcut_path)
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
    logger.info('Shortcut created: %s', shortcut_path)
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
                logger.error(f"Cannot remove {file}: {e}")
    return True


def get_icon_path(ext):
    full_path = Path(file_tools.get_assets(f"icons/icon.{ext}"))
    if not full_path.exists():
        logger.error(f"Cannot find icon: {full_path}")
        return
    icon_in_config = app_dirs.config_dir('icons', full_path.name)
    if icon_in_config.exists():
        return icon_in_config.as_posix()
    icon_in_config.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(full_path, icon_in_config)
    return icon_in_config.as_posix()
