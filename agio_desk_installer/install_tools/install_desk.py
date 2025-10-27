import os
import subprocess
from pathlib import Path

DEFAULT_VENV_PYTHON_VERSION = '3.11.*'
DEFAULT_VENV_PACKAGES = (
    # default
    'agio_core',
    'agio_desk',
    'agio_broker',
    # temporary common packages
    'agio_pipe',
    'agio_publish_simple',
    'agio_launcher'
)
ASSETS_DIR = Path(__file__).resolve().parent.parent.joinpath('assets')
BIN_EXT = '.exe' if os.name == 'nt' else ''


def get_uv_executable() -> str:
    uv_exec = ASSETS_DIR.joinpath('uv'+BIN_EXT)
    return uv_exec.as_posix()


def _exec_uv_command(command: list[str], workdir: str = None) -> None:
    cmd = [
        get_uv_executable(),
        *command,
    ]
    workdir = workdir or get_default_venv_path()
    subprocess.run(cmd, cwd=workdir)


def create_default_venv():
    # get dir
    workdir = get_default_venv_path()
    # init project
    _exec_uv_command(['init', '--bare', '--python', DEFAULT_VENV_PYTHON_VERSION], workdir=workdir)
    # create venv
    _exec_uv_command(['init', '--venv'], workdir=workdir)
    return workdir


def get_agio_store_dir() -> str:
    if os.name == 'nt':
        return os.path.expandvars(r'%APPDATA%\Local\agio')
    else:
        return os.path.expanduser('~/.local/share/agio')


def get_default_venv_path():
    env_path = Path(get_agio_store_dir(), 'default-env')
    env_path.mkdir(parents=True, exist_ok=True)
    return env_path.as_posix()


def install_packages(*pkgs, workdir=None):
    _exec_uv_command(['pip', 'install', '--refresh', '--quiet', *pkgs], workdir=workdir)
    # --refresh-package


def get_user_bin_path() -> str:
    if os.name == 'nt':
        path = Path(os.path.expandvars(r'%APPDATA%\Local\Microsoft\WindowsApps'))
    else:
        path = Path('~/.local/bin').expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path.as_posix()


def make_global_command_executable(exec_file: str, file_name: str = None) -> str:
    bin_path_dir = Path(get_user_bin_path())
    bin_path_dir.mkdir(parents=True, exist_ok=True)
    binary_file_name = file_name or Path(exec_file).name
    binary_file_path = Path(bin_path_dir, binary_file_name)
    Path(exec_file).symlink_to(binary_file_path)
    return binary_file_path.as_posix()


def get_package_list():
    # TODO get whl list from server
    return DEFAULT_VENV_PACKAGES


def get_agio_bin_path(project_root: str)-> str:
    if os.name == 'nt':
        return Path(project_root, '.venv', 'Scripts', 'agio.exe').as_posix()
    else:
        return Path(project_root, '.venv', 'bin', 'agio.exe').as_posix()


def install():
    # create new venv
    workdir = create_default_venv()
    # get package list
    pacakge_list = get_package_list()
    # install packages
    install_packages(*pacakge_list, workdir=workdir)
    # create global command bin
    agio_exec = get_agio_bin_path(workdir)
    if not Path(agio_exec).exists():
        raise RuntimeError('agio executable not found')
    make_global_command_executable(agio_exec)