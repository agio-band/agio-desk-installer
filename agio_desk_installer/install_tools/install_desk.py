import logging
import os
import subprocess
from pathlib import Path

from agio.tools import app_dirs
from agio_desk_installer.install_tools import repository
from agio_desk_installer.install_tools.customization import parse_line

logger = logging.getLogger(__name__)


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
ASSETS_DIR = Path(__file__, '..').resolve().parent.joinpath('assets')
BIN_EXT = '.exe' if os.name == 'nt' else ''

# variables
def get_uv_executable() -> str:
    # return 'uv'
    uv_exec = ASSETS_DIR.joinpath('uv'+BIN_EXT)
    return str(uv_exec)


def get_agio_bin_path(project_root: str|Path)-> str:
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
    workdir = Path(workdir or app_dirs.default_env_dir())
    logger.debug(f'CMD: {" ".join(cmd)}')
    envs = os.environ.copy()
    envs['VIRTUAL_ENV'] = workdir.joinpath('.venv').as_posix()
    subprocess.run(cmd, cwd=workdir.as_posix(), env=envs)


# install
def create_default_venv(env_path: str = None) -> Path:
    # get dir
    env_path = Path(env_path or app_dirs.default_env_dir())
    logger.debug("Creating default venv")
    env_path.mkdir(parents=True, exist_ok=True)
    # init project
    if not env_path.joinpath('pyproject.toml').exists():
        _exec_uv_command(['init', '--bare', '--python', DEFAULT_VENV_PYTHON_VERSION], workdir=str(env_path))
    # create venv
    _exec_uv_command(['venv', '--clear'], workdir=str(env_path))
    return env_path


def install_packages(*pkgs, workdir, refresh_packages=False):
    cmd = ['pip', 'install']#, '--quiet']
    if refresh_packages:
        cmd.append('--refresh') # --refresh-package
    _exec_uv_command([*cmd, *pkgs], workdir=workdir)


def make_global_command_executable(exec_file: str, file_name: str = None) -> str:
    """Create global "agio" command"""
    bin_path_dir = app_dirs.user_binary_path_dir()
    bin_path_dir.mkdir(parents=True, exist_ok=True)
    binary_file_name = file_name or Path(exec_file).name
    binary_file_path = Path(bin_path_dir, binary_file_name)
    if binary_file_path.exists():
        binary_file_path.unlink()
    logger.info(f'Creating link {binary_file_path} -> {exec_file}')
    Path(binary_file_path).symlink_to(exec_file)
    return str(binary_file_path)


def get_package_list(versions: list[str] = None):
    custom_versions = {}
    if versions is not None:
        for custom_version in versions:
            pkg, data = parse_line(custom_version)
            custom_versions[pkg] = data
    for pkg_name in DEFAULT_VENV_PACKAGES:
        kwargs = {}
        url = repository.package_name_to_agio_band_git_repository_url(pkg_name)
        custom_version = custom_versions.get(pkg_name, {})
        if custom_version:
            kwargs[custom_version['ref_type']] = custom_version['value']
        yield repository.get_package_installation_url(url, **kwargs)


# main
def install(path_to_install: str = None, package_versions: list[str] = None, **kwargs) -> dict:
    # create new venv
    workdir = create_default_venv(path_to_install)
    # get package list
    pacakge_list = get_package_list(package_versions)
    # install packages
    install_packages(*pacakge_list, workdir=workdir)
    # create global command bin
    agio_exec = get_agio_bin_path(workdir)
    if not Path(agio_exec).exists():
        raise FileNotFoundError(f'agio executable not found {agio_exec}')
    make_global_command_executable(agio_exec)
    return dict(
            executable=agio_exec,
            install_path=workdir,
        )
