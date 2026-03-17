import logging
import platform
import shutil
from pathlib import Path

from agio.tools import local_dirs
from . import install_desk, user_tools, file_tools

logger = logging.getLogger(__name__)


def start_install(**kwargs):
    """Example:
    {
      'path_to_install': '/home/username/agio',
      'add_desktop_shortcut': True,
      'add_main_menu_shortcut': True,
      'package_versions': ('agio-core:branch=dev', 'agio-desk:commit=d947745')
    }
    """
    local_dirs.save_global_config(kwargs)
    logger.info('Start installation...')
    try:
        result = install_desk.install(**kwargs)
    except Exception as e:
        logger.exception('Installation failed.')
        raise
    # create scripts
    scripts_dir = file_tools.get_assets('scripts', platform.system().lower())
    context = {
        'config_dir': local_dirs.config_dir().as_posix(),
        'agio_executable': result['executable']
    }
    install_desk.copy_scripts(scripts_dir, local_dirs.binary_files_dir(), context)
    logger.info("Executable file %s", result['executable'])
    # copy UV
    install_desk.copy_uv(local_dirs.binary_files_dir())
    # create shortcuts
    kw = dict(
        shortcut_name='agio.desk',
        # executable_file=result['executable'],
        executable_file=str(local_dirs.binary_files_dir('agio-desk.cmd')),
        workdir=result['install_path'],
        # args=['desk']
    )
    logger.info('Create Shortcuts...')
    if kwargs.get('add_desktop_shortcut'):
        user_tools.create_desktop_shortcut(**kw)
    if kwargs.get('add_main_menu_shortcut'):
        user_tools.create_main_menu_shortcut(**kw)
    logger.info('Installing done!')


def uninstall(delete_user_prefs=False):
    info = local_dirs.get_global_config()
    install_path = info.get('path_to_install')
    if install_path:
        install_path = Path(install_path)
        if install_path.is_dir():
            shutil.rmtree(install_path)
    if delete_user_prefs:
        local_dirs.delete_global_config_file()


