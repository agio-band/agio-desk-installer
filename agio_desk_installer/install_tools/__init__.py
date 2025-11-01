import logging
import shutil
from pathlib import Path

from . import install_desk, user_tools
from .user_tools import save_info_file, load_info_file, delete_info_file

logger = logging.getLogger(__name__)


def start_install(**kwargs):
    # {
    #   'path_to_install': '/home/paul/agio/agio-desk',
    #   'add_desktop_shortcut': True,
    #   'add_main_menu_shortcut': True,
    #   'package_versions': ('agio-core:branch=dev', 'agio-pipe:tag=0.0.1', 'agio-desk:commit=d947745')
    # }
    print('Start installation...', flush=True)
    result = install_desk.install(**kwargs)
    kw = dict(
        shortcut_name='agio.desk',
        executable_file=result['executable'],
        icon='',
        workdir=result['install_path'],
        args=['desk']
    )
    print('Create Shortcuts...', flush=True)
    if kwargs.get('add_desktop_shortcut'):
        user_tools.create_desktop_shortcut(**kw)
    if kwargs.get('add_main_menu_shortcut'):
        user_tools.create_main_menu_shortcut(**kw)
    save_info_file(kwargs)
    print('Installing done!', flush=True)


def uninstall(delete_user_prefs=False):
    info = load_info_file()
    install_path = info.get('path_to_install')
    if install_path:
        install_path = Path(install_path)
        if install_path.is_dir():
            shutil.rmtree(install_path)
    if delete_user_prefs:
        delete_info_file()


