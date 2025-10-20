import logging
import sys
import subprocess
import zipfile

import requests
from agio_desk_installer.tools import downloader, exceptions, installers
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

if sys.platform.startswith("win"):
    import winreg

# WinFsp
def check_winfsp() -> bool:
    try:
        output = subprocess.check_output(
            ["sc", "query", "WinFsp.Launcher"],
            stderr=subprocess.STDOUT,
            text=True
        )
        if "RUNNING" in output:
            return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        print("WinFsp.Launcher not found")
        return False
    return False

def winfsp_tool():
    if check_app_installed("WinFsp"):
        print("WinFsp check.", flush=True)
        if check_winfsp():
            raise exceptions.WinFspIsRunning
    else:
        print("WinFsp not installed.", flush=True)
        winfsp_msi = downloader.download_winfsp_installer()
        try:
            print("Try to install WinFsp", flush=True)
            installers.install_winfsp(winfsp_msi)
        except Exception as e:
            raise exceptions.WinFspNotInstalling from e

def check_app_installed(app_name: str) -> str | bool:
    uninstall_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for path in uninstall_paths:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                num_subkeys, _, _ = winreg.QueryInfoKey(key)
                for i in range(num_subkeys):
                    subkey_name = winreg.EnumKey(key, i)
                    try:
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            if app_name.lower() in name.lower():
                                try:
                                    version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                                    return version
                                except FileNotFoundError:
                                    return True
                    except (FileNotFoundError, OSError):
                        continue
        except FileNotFoundError:
            continue
    return False

# Drive
def get_drive_binary(path: str, name: str) -> str | None:
    bin_path = os.path.join(path, name)
    return  bin_path if os.path.isfile(bin_path) else None

def drive_tool(dest_path: str, add_shortcut: bool, version: str = "latest" ) -> None:
    latest_ver = downloader.download_last_version()
    is_run = drive_is_launched()
    if is_run:
        print("please shot down drive, us run: ", is_run, flush=True)
        raise exceptions.HaveLatestVersion
    #тут напишу обработчик сетингов разных версий, когда получу сетинги
    else:
        print("Download agio-drive.", flush=True)
        agio_drive_bin = downloader.download_agio_drive_bin(version)
        print(f"Agio-drive downloading in: {agio_drive_bin}, ver: {latest_ver}", flush=True)
        try:
            if not dest_path.rstrip("\\/").endswith("agio-drive"):
                dest_path = os.path.join(dest_path, "agio-drive")
            if os.path.exists(dest_path):
                print(f"dest path: {dest_path}", flush=True)
                shutil.rmtree(dest_path)
                print(f"Old folder removed: {dest_path}", flush=True)

            os.makedirs(dest_path, exist_ok=True)
            shutil.move(agio_drive_bin, dest_path)

            print("Move agio-drive in: " + dest_path, flush=True)
        except Exception as e:
            raise e
        if add_shortcut:
            installers.create_shortcut_windows(f"agio.drive.lnk", dest_path)

        print(f'Build agio.drive installer v{version} in {dest_path}', flush=True)

def drive_tool_linux(version: str, dest_path: str, add_shortcut: bool) -> None:
    latest_ver = downloader.download_last_version()
    is_run = drive_is_launched()
    if is_run:
        print("please shot down drive, us run: ", is_run, flush=True)
    #тут напишу обработчик сетингов разных версий, когда получу сетинги
    else:
        print("Download agio-drive.", flush=True)
        agio_drive_bin = downloader.download_agio_drive_linux(version)
        print(f"Agio-drive downloading in: {agio_drive_bin}, ver: {latest_ver}", flush=True)
        try:
            if os.path.exists(dest_path):
                print(f"Existing path found, removing: {dest_path}", flush=True)
                shutil.rmtree(dest_path)
            os.makedirs(dest_path, exist_ok=True)
            drive_path = os.path.join(dest_path, "agio-drive")
            shutil.move(agio_drive_bin, drive_path)
            print("Move agio-drive in: " + drive_path, flush=True)
        except Exception as e:
            raise e
        if add_shortcut:
            installers.create_shortcut_linux(f"agio.drive", drive_path)

        print(f'Build agio.drive installer v{version} in {dest_path}', flush=True)

def drive_is_launched() -> bool:
    try:
        resp = requests.get('http://localhost:9085/swagger/index.html', timeout=0.1)
        logger.warning('check code', resp.status_code)
        return resp.status_code == 200
    except Exception:
        return False


# ffmpeg
def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ffmpeg(install_dir: str = None):
    install_dir = Path(install_dir or r"C:\ffmpeg")
    print(f"Installing ffmpeg: {install_dir}", flush=True)
    dest_path = Path(os.getenv("TEMP", ".")) / "ffmpeg.zip"
    archive = downloader.download_ffmpeg_win(dest_path)
    print(f"Extracting in {archive}")

def ffmpeg_tools():
    if check_ffmpeg():
        print("ffmpeg installed", flush=True)
    else:
        print("ffmpeg not installed", flush=True)
        install_ffmpeg()