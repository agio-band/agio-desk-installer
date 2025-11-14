import logging
import os
import subprocess
from pathlib import Path

from agio.tools import app_dirs
from agio_desk_installer.install_tools import repository, file_tools
from agio_desk_installer.install_tools.customization import parse_line

logger = logging.getLogger(__name__)


DEFAULT_VENV_PYTHON_VERSION = '>=3.11.0, <3.12'
BUNDLES_URL = 'https://storage.yandexcloud.net/agio-public/pipe-config/installer-bundles.json'
DEFAULT_VENV_PACKAGES = (
    'agio_core',
    'agio_desk',
    'agio_broker',
    'agio_drive',
)

BIN_EXT = '.exe' if os.name == 'nt' else ''

# variables
def get_uv_executable() -> str:
    uv_exec = file_tools.get_assets('uv'+BIN_EXT)
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
    workdir = Path(workdir or app_dirs.default_env_install_dir())
    logger.debug(f'CMD: {" ".join(cmd)}')
    envs = os.environ.copy()
    envs.pop('VIRTUAL_ENV', None)
    subprocess.run(cmd, cwd=workdir.as_posix(), env=envs)


# install
def create_default_venv(env_path: str|Path = None) -> Path:
    # get dir
    env_path = Path(env_path or app_dirs.default_env_install_dir())
    logger.debug("Creating default venv")
    env_path.mkdir(parents=True, exist_ok=True)
    # init project
    if not env_path.joinpath('pyproject.toml').exists():
        _exec_uv_command(['init', '--bare', '--python', DEFAULT_VENV_PYTHON_VERSION], workdir=str(env_path))
    # create venv
    _exec_uv_command(['venv', '--clear'], workdir=str(env_path))
    return env_path


def install_packages(*pkgs, workdir, refresh_packages=True):
    print('Installing packages:')
    for p in pkgs:
        print(p, flush=True)
    cmd = ['pip', 'install']
    if refresh_packages:
        cmd.append('--reinstall')
    _exec_uv_command([*cmd, *pkgs], workdir=workdir)


def make_global_command_executable(exec_file: str, file_name: str = None) -> str:
    """Create global "agio" command"""
    bin_path_dir = app_dirs.user_binary_path_dir()
    bin_path_dir.mkdir(parents=True, exist_ok=True)
    binary_file_name = file_name or Path(exec_file).name
    binary_file_path = Path(bin_path_dir, binary_file_name)
    if binary_file_path.exists() or binary_file_path.is_symlink():
        binary_file_path.unlink()
    logger.info(f'Creating link {binary_file_path} -> {exec_file}')
    Path(binary_file_path).symlink_to(exec_file)
    # Path(binary_file_path).hardlink_to(exec_file)
    return str(binary_file_path)


def get_package_list(versions: dict = None):
    if versions:
        print('Selected versions:', flush=True)
        for k, v in versions.items():
            print(v['raw'], flush=True)
    else:
        print('Use latest releases for all packages:', flush=True)
    for pkg_name in DEFAULT_VENV_PACKAGES:
        # break
        kwargs = {}
        url = repository.package_name_to_agio_band_git_repository_url(pkg_name)
        custom_version = versions.get(pkg_name, {})
        if custom_version:
            kwargs[custom_version['ref_type']] = custom_version['value']
        yield repository.get_package_installation_url(url, **kwargs)


def execute_workspace_on_install_callbacks(path):
    from agio.core.workspaces import AWorkspaceManager

    manager = AWorkspaceManager(root=path)
    for pkg in manager.iter_installed_packages():
        pkg.execute_package_callback('on_installed', manager)

# main
def install(install_path: str = None, package_versions: list[str] = None, **kwargs) -> dict:
    # get package list
    logger.info('Collecting packages...')
    pacakge_list = list(get_package_list(package_versions))
    # install packages
    logger.info('Packages to install:')
    for pkg_name in pacakge_list:
        logger.info(pkg_name)
    # create new venv
    default_venv_dir = app_dirs.default_env_install_dir(install_path)
    workdir = create_default_venv(default_venv_dir)
    install_packages(*pacakge_list, workdir=workdir)
    # execute packages on installation callbacks
    execute_workspace_on_install_callbacks(workdir)
    # create global command bin
    agio_exec = get_agio_bin_path(workdir)
    logger.info('agio executable: %s', agio_exec)
    if not Path(agio_exec).exists():
        raise FileNotFoundError(f'Executable not found {agio_exec}')
    make_global_command_executable(agio_exec)
    return dict(
            executable=agio_exec,
            install_path=workdir,
        )
