import logging
import shutil
import sys

from PySide6.QtWidgets import QMessageBox

PLATFORM = sys.platform.lower()
logger = logging.getLogger(__name__)

def before_install_linux(parent, **kwargs):
    if not _check_build_tools():
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("Installation requirements")
        msg_box.setText(
            "Please? install build tools 'build-essential' before continue. "
            "Press OK to continue or cancel to stop installation process."
            "\n\nExample: sudo apt install -y build-essential")
        msg_box.setDetailedText('sudo apt install -y build-essential')
        msg_box.setIcon(QMessageBox.Question)

        save_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)

        msg_box.exec()

        clicked = msg_box.clickedButton()
        if clicked == save_btn:
            return True
        elif clicked == cancel_btn:
            return False
    return True


# def after_install_linux(parent, **kwargs):
#     pass


def before_install_windows(parent, **kwargs):
    return True


def _default_callback(parent, **kwargs):
    return True



# def after_install_windows(parent, **kwargs):
#     return True


def get_callback(name: str):
    func_name = f'{name}_{PLATFORM}'
    print(func_name)
    clb = globals().get(func_name) or _default_callback
    if clb:
        print('OK', clb)
        return clb
    else:
        print('NOT FOUND')
        logger.debug('No callback defined for platform %s', PLATFORM)
        return None

######### TOOLS


def _check_build_tools(tools: tuple[str, ...] = ("gcc", "g++", "make")) -> bool:
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        logger.debug(f"missing tools: {', '.join(missing)}")
        return False
    return True