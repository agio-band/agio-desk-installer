import os
import subprocess
from pathlib import Path
from agio.tools import app_dirs

DEFAULT_VENV_PYTHON_VERSION = '>=3.11.0, <3.12'
DEFAULT_VENV_PACKAGES = (
    # default
    'agio_core',
    'agio_desk',
    'agio_broker',
    # temporary common packages
    # 'agio_drive', # SOON
    'agio_pipe',
    'agio_publish_simple',
    'agio_launcher'
)
ASSETS_DIR = Path(__file__).resolve().parent.joinpath('assets')
BIN_EXT = '.exe' if os.name == 'nt' else ''

# variables
def get_uv_executable() -> str:
    # return 'uv'
    uv_exec = ASSETS_DIR.joinpath('uv'+BIN_EXT)
    return str(uv_exec)


# def get_agio_installation_path() -> str:
#     return str(app_dirs.install_dir())
    # if os.name == 'nt':
    #     return os.path.expandvars(r'%APPDATA%\Local\agio')
    # else:
    #     return os.path.expanduser('~/.local/share/agio')


# def get_default_venv_path():
#     env_path = app_dirs.default_env_dir()
#     return str(env_path)


# def get_user_bin_path() -> str:
#     path = app_dirs.user_binary_path_dir()
#     return str(path)


def get_agio_bin_path(project_root: str)-> str:
    if os.name == 'nt':
        return Path(project_root, '.venv', 'Scripts', 'agio.exe').as_posix()
    else:
        return Path(project_root, '.venv', 'bin', 'agio').as_posix()

# utils
def _exec_uv_command(command: list[str], workdir: str = None) -> None:
    cmd = [
        get_uv_executable(),
        *command,
    ]
    workdir = workdir or app_dirs.default_env_dir()
    print('CMD', ' '.join(cmd))
    subprocess.run(cmd, cwd=workdir)


# install
def create_default_venv():
    # get dir
    env_path = app_dirs.default_env_dir()
    env_path.mkdir(parents=True, exist_ok=True)
    # init project
    _exec_uv_command(['init', '--bare', '--python', DEFAULT_VENV_PYTHON_VERSION], workdir=str(env_path))
    # create venv
    _exec_uv_command(['venv'], workdir=str(env_path))
    return env_path


def install_packages(*pkgs, workdir, refresh_packages=False):
    cmd = ['pip', 'install', '--refresh', '--quiet']
    if refresh_packages:
        cmd.append('--refresh') # --refresh-package
    _exec_uv_command([*cmd, *pkgs], workdir=workdir)



def make_global_command_executable(exec_file: str, file_name: str = None) -> str:
    bin_path_dir = app_dirs.user_binary_path_dir()
    bin_path_dir.mkdir(parents=True, exist_ok=True)
    binary_file_name = file_name or Path(exec_file).name
    binary_file_path = Path(bin_path_dir, binary_file_name)
    Path(exec_file).symlink_to(binary_file_path)
    return str(binary_file_path)


def get_package_list():
    # TODO get whl list from server
    return DEFAULT_VENV_PACKAGES

# main
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