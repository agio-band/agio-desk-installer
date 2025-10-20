import shutil
import subprocess
import os


def install_winfsp(installer_path: str) -> None:

    if not os.path.isfile(installer_path):
        raise FileNotFoundError(f"Installer not found: {installer_path}")

    print(f"Installing WinFsp from {installer_path} ...")

    cmd = [
        "msiexec",
        "/i", installer_path,
        "/quiet",
        "/norestart"
    ]
    subprocess.run(cmd, check=True)
    print("WinFsp installation completed successfully.")

def create_shortcut_windows(file_name: str, target: str, arguments: str = ''):
    from win32com.client import Dispatch

    icon_path = os.path.join(os.path.realpath(__file__+'../../../..'), 'assets/icons/icon.ico')

    icon_path = shutil.copy(icon_path, target)
    exe_path = os.path.normpath(target.strip()) + "\\agio-drive.exe"
    work_dir = os.path.dirname(exe_path)
    shell = Dispatch('WScript.Shell')
    desktop = shell.SpecialFolders("Desktop")
    shortcut_path = os.path.join(desktop, f"{file_name}.lnk")

    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        print("old shortcut file deleted", flush=True)
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = exe_path
    shortcut.Arguments = arguments
    shortcut.WorkingDirectory = work_dir
    shortcut.IconLocation = icon_path.replace('/', '\\')
    shortcut.save()
    print("Shortcut created successfully.")


def create_shortcut_linux(file_name: str, target: str, arguments: str = ''):
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    work_dir = os.path.dirname(target)
    os.makedirs(desktop_dir, exist_ok=True)
    shortcut_path = os.path.join(desktop_dir, f"{file_name}.desktop")
    lines = [
        "[Desktop Entry]",
        f"Name={file_name}",
        f"Exec=\"{os.path.abspath(target)}\" {arguments}".strip(),
        f"Path={os.path.abspath(work_dir)}",
        f"Icon={os.path.abspath('assets/icons/icon.ico')}",
        "Terminal=false",
        "Type=Application",
        "StartupNotify=true"
    ]
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    os.chmod(shortcut_path, 0o755)
    print(f"Shortcut created successfully: {shortcut_path}", flush=True)


def create_shortcut_mac(file_name: str, target: str, work_dir: str, arguments: str = ''):
    raise NotImplementedError


def install_drive_windows():
    ...


def uninstall_drive_windows():
    ...

