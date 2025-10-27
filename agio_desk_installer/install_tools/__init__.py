
def start_install(**kwargs):
    # {'path_to_install': '/home/paul/agio/agio-desk', 'add_desktop_shortcut': True, 'add_main_menu_shortcut': True, 'versions': None, 'package_versions': ('agio-core:branch=dev', 'agio-pipe:tag=0.0.1', 'agio-desk:commit=d947745')}
    print('Installation options:')
    from pprint import pprint

    pprint(kwargs)
    # TODO