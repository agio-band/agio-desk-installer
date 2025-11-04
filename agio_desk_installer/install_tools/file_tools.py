import inspect
import os
import sys
from pathlib import Path

IS_FROZEN = globals().get('__compiled__', None)
ASSET_DIR = Path(__file__, '../../../assets' if IS_FROZEN else '../../assets').resolve()


def get_executable() -> list[str]:
    if IS_FROZEN:
        return [sys.argv[0]]
    else:
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        return [sys.executable, os.path.abspath(filename)]


def get_assets(*args) -> str:
    path = Path(ASSET_DIR, *args)
    if not path.exists():
        raise FileNotFoundError(path)
    return path.as_posix()