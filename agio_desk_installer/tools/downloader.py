import tempfile
from pathlib import Path

import requests
import os


TEMP = tempfile.mkdtemp()
drive_url = "https://storage.yandexcloud.net/agio-public/drive/{version}/windows/amd64/bin/agio-drive.exe"
drive_url_linux = "https://storage.yandexcloud.net/agio-public/drive/{version}/linux/amd64/bin/agio-drive"
ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

def download_agio_drive_bin(version: str = None) -> str:
    version = version or "latest"
    dest = os.path.join(TEMP, "agio-drive.exe")
    full_url = drive_url.format(version=version)
    with requests.get(full_url, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print("Done loading agio-drive for windows.", flush=True)
    return dest

def download_agio_drive_linux(version, url: str = drive_url_linux) -> str:
    version = version or "latest"
    dest = os.path.join(TEMP, "agio-drive")
    url = drive_url_linux.format(version=version)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print("Done loading agio-drive for linux.", flush=True)
    return dest

def download_winfsp_installer(dest: str = TEMP) -> str:

    url = get_latest_winfsp_installer_url()
    os.makedirs(dest, exist_ok=True)
    filename = os.path.basename(url)
    dest = os.path.join(dest, filename)

    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0

            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = downloaded / total_size * 100
                            print(f"\rdownload WinFsp: {percent:.1f}%", end="", flush=True)

        return dest
    except requests.RequestException as e:
        raise RuntimeError(f"Download error: {e}") from e

def get_latest_winfsp_installer_url() -> str:

    api_url = "https://api.github.com/repos/winfsp/winfsp/releases/latest"
    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"error GitHub API: {e}") from e

    data = resp.json()
    assets = data.get("assets", [])
    for asset in assets:
        name = asset.get("name", "")
        if name.lower().endswith(".msi"):
            download_url = asset.get("browser_download_url")
            if download_url:
                return download_url

    raise RuntimeError("Dont find .msi inst WinFsfp in latest release")

def download_last_version():
    url = "https://storage.yandexcloud.net/agio-public/drive/VERSION"

    response = requests.get(url)
    response.raise_for_status()
    content = response.text.strip()
    return content

def download_ffmpeg_win(dest_path: str | Path, ffmpeg_url: str = ffmpeg_url):
    print(f"downloading ffmpeg", end="", flush=True)
    # with requests.get(ffmpeg_url, stream=True) as r:
    #     r.raise_for_status()
    #     total_size = int(r.headers.get("content-length", 0))
    #     downloaded = 0
    #     chunk_size = 8192
    #
    #     with open(dest_path, "wb") as f:
    #         for chunk in r.iter_content(chunk_size=chunk_size):
    #             if chunk:
    #                 f.write(chunk)
    #                 downloaded += len(chunk)
    #                 if total_size:
    #                     percent = downloaded * 100 / total_size
    #                     print(f"downloading: {percent:.1f}%", end="", flush=True)
    return dest_path