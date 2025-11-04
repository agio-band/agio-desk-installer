import logging
import shutil
from pathlib import Path

from . import install_desk, user_tools
from agio.tools import app_dirs

logger = logging.getLogger(__name__)


def start_install(**kwargs):
    # {
    #   'path_to_install': '/home/paul/agio/agio-desk',
    #   'add_desktop_shortcut': True,
    #   'add_main_menu_shortcut': True,
    #   'package_versions': ('agio-core:branch=dev', 'agio-pipe:tag=0.0.1', 'agio-desk:commit=d947745')
    # }
    app_dirs.save_global_config(kwargs)
    print('Start installation...', flush=True)
    result = install_desk.install(**kwargs)
    print("EXECUTABLE FILE", result['executable'], flush=True)
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
    print('Installing done!', flush=True)


def uninstall(delete_user_prefs=False):
    info = app_dirs.get_global_config()
    install_path = info.get('path_to_install')
    if install_path:
        install_path = Path(install_path)
        if install_path.is_dir():
            shutil.rmtree(install_path)
    if delete_user_prefs:
        app_dirs.delete_global_config_file()


