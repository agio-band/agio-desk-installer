import click

# agio-drive-setup --install-dir ~/agio --add-shortcuts --add-shortcut_in_setting
@click.command()
@click.option("-i", "--install-dir", type=str, required=False, default=None, help="dir for installation")
@click.option("-a", "--add-shortcut", is_flag=True, required=False, default=True, help="add a shortcut in desktop")
@click.option("-m", "--add-shortcut_in_setting", is_flag=True, required=False, default=False, help="add a shortcut in settings")
@click.option("-r", "--autorun", is_flag=True, required=False, default=True, help="autorun")
@click.option("-d", "--open_docs", is_flag=True, required=False, default=False, help="open documentation")
@click.option("-s", "--open_settings", is_flag=True, required=False, default=False, help="open settings")
def install(
        install_dir: str,
        add_shortcut: bool,
        add_shortcut_in_settings: bool,
        autorun: bool,
        open_docs: bool,
        open_settings: bool
) -> None:
    from main import main
    main(
        path_to_install=install_dir,
        add_shortcut=add_shortcut,
        add_shortcut_menu=add_shortcut_in_settings,
        autorun=autorun,
        open_docs=open_docs,
        open_settings=open_settings
    )

