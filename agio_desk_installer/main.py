import json
import os
import sys
import traceback
from pathlib import Path
import logging
from PySide6.QtCore import *
from PySide6.QtCore import QSize, QProcess
from PySide6.QtGui import *
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import *
import requests

from agio.tools.paths import open_path
from agio_desk_installer.install_tools import setup_logs, start_install, customization, file_tools
from agio.tools import app_dirs, process_utils
from agio_desk_installer.labels import WELCOME_TEXT, DONE_TEXT

logger = logging.getLogger(__name__)
IS_WINDOWS = os.name == 'nt'


class AgioDeskInstallerDialog(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.setWindowTitle("agio.desk Installer")
        icon = self.prepare_svg(file_tools.get_assets("icons/favicon-o-knob-16.svg"))
        self.setWindowIcon(icon)

        self.centralwidget = QWidget()

        self.central_ly = QVBoxLayout(self.centralwidget)
        self.central_ly.setContentsMargins(0, 0, 0, 0)
        self.central_ly.setSpacing(0)

        self.top_widget = QWidget(self.centralwidget)
        self.top_widget.setObjectName('darkWidget')
        self.top_widget.setMinimumSize(QSize(0, 100))
        # welcome text
        self.top_ly = QHBoxLayout(self.top_widget)
        self.top_ly.setContentsMargins(30, 10, 30, 10)
        self.label_welcome = QLabel()
        font = QFont()
        font.setPixelSize(14)
        font.setBold(True)
        self.label_welcome.setFont(font)
        self.top_ly.addWidget(self.label_welcome)
        # icon
        self.label_icon = QSvgWidget(file_tools.get_assets("icons/logo.svg"))
        self.label_icon.setFixedSize(QSize(200, 90))
        self.top_ly.addWidget(self.label_icon)

        self.central_ly.addWidget(self.top_widget)
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName('separator')
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.central_ly.addWidget(self.line)
        # book
        self.book_widget = QStackedWidget(self.centralwidget)
        # page1
        self.page_1 = QWidget()
        self.page1_ly = QVBoxLayout(self.page_1)
        self.page1_ly.setContentsMargins(30, 20, 30, 20)

        self.label_step1 = QLabel(WELCOME_TEXT)
        self.label_step1.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.page1_ly.addWidget(self.label_step1)

        self.page1_but = QHBoxLayout()
        self.page1_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))


        self.next_btn = QPushButton("Next", clicked=self.on_click_next)
        self.page1_but.addWidget(self.next_btn)
        self.page1_ly.addLayout(self.page1_but)
        self.page1_ly.setStretch(0, 1)
        self.book_widget.addWidget(self.page_1)

        # page2
        self.page_2 = QWidget()
        self.settings_ly = QVBoxLayout()
        self.settings_ly.setContentsMargins(30, 20, 30, 20)
        self.page_2.setLayout(self.settings_ly)

        self.formLayout = QFormLayout()
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.browse_ly = QHBoxLayout()
        self.installation_path_le = QLineEdit()
        self.installation_path_le.setPlaceholderText("Installation Path")
        self.browse_ly.addWidget(self.installation_path_le)
        self.toolButton = QPushButton("Browse...", clicked=self.on_click_browse)
        self.browse_ly.addWidget(self.toolButton)

        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.browse_ly)
        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, QLabel("Destination"))

        self.add_desktop_shortcut_cbx = QCheckBox('', checked=True)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.add_desktop_shortcut_cbx)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, CheckBoxLabel(self.add_desktop_shortcut_cbx, "Add Desktop Shortcut"))

        self.add_menu_shortcut_cbx = QCheckBox('', checked=True)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.add_menu_shortcut_cbx)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, CheckBoxLabel(self.add_menu_shortcut_cbx, "Add Main Menu Shortcut"))

        self.select_bundle_cbb = BundleSelectorWidget()
        self.bundle_lb = QLabel("Bundle")
        self.select_bundle_cbb.setVisible(bool(os.getenv('DEBUG')))
        self.bundle_lb.setVisible(bool(os.getenv('DEBUG')))
        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.bundle_lb)
        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.select_bundle_cbb)
        self.custom_versions_te = QTextEdit()
        self.custom_versions_te.setReadOnly(False)
        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.custom_versions_te)
        self.select_bundle_cbb.currentTextChanged.connect(self.on_bundle_changed)
        self.custom_versions_te.setPlaceholderText('Custom versions')
        self.custom_versions_te.hide()
        self.custom_versions_te.setMaximumWidth(200)

        self.bundle_content_lb = QLabel('')
        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.bundle_content_lb)
        self.bundle_content_lb.hide()
        self.bundle_content_lb.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.settings_ly.addLayout(self.formLayout)

        self.page2_but = QHBoxLayout()
        self.page2_but.setContentsMargins(0, 0, 0, 0)
        self.page2_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.cancel = QPushButton("Cancel", clicked=self.on_click_cancel)
        self.page2_but.addWidget(self.cancel)

        self.install = QPushButton("Install", clicked=self.on_click_install)
        self.page2_but.addWidget(self.install)
        self.settings_ly.addLayout(self.page2_but)

        self.book_widget.addWidget(self.page_2)
        # page3
        self.page_3 = QWidget()
        self.logs_ly = QVBoxLayout(self.page_3)
        self.logs_ly.setContentsMargins(30, 20, 30, 20)
        self.output_logs = QTextBrowser()
        self.logs_ly.addWidget(self.output_logs)

        self.logs_but = QHBoxLayout()
        self.logs_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.back = QPushButton("Back", clicked=self.on_click_back)
        self.logs_but.addWidget(self.back)
        self.back.hide()

        self.cancel_3 = QPushButton("Cancel", clicked=self.on_click_cancel_install)
        self.logs_but.addWidget(self.cancel_3)
        self.logs_ly.addLayout(self.logs_but)

        self.book_widget.addWidget(self.page_3)
        # page4
        self.page_4 = QWidget()
        self.final_ly = QVBoxLayout(self.page_4)
        self.final_ly.setContentsMargins(30, 20, 30, 20)
        self.page_4.setLayout(self.final_ly)

        self.thanks_lb = QLabel()
        self.thanks_lb.setAlignment(
            Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.thanks_lb.setTextFormat(Qt.RichText)
        self.thanks_lb.setText(DONE_TEXT)
        self.thanks_lb.setOpenExternalLinks(True)
        self.final_ly.addWidget(self.thanks_lb)
        # buttons
        self.fin_but = QHBoxLayout()
        self.fin_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.finish_but = QPushButton("Close", clicked=self.on_click_finish)
        self.fin_but.addWidget(self.finish_but)
        self.final_ly.addLayout(self.fin_but)
        self.final_ly.setStretch(0, 1)

        self.book_widget.addWidget(self.page_4)

        # other
        self.central_ly.addWidget(self.book_widget)

        self.setCentralWidget(self.centralwidget)

        self.set_page_welcome()
        self.resize(800, 500)
        self.init_ui()

        # self.custom_versions = {}
        self.proc: QProcess|None = None

        # debug shortcuts
        QShortcut(QKeySequence("Alt+1"), self, activated=self.set_page_welcome)
        QShortcut(QKeySequence("Alt+2"), self, activated=self.set_page_settings)
        QShortcut(QKeySequence("Alt+3"), self, activated=self.set_page_logs)
        QShortcut(QKeySequence("Alt+4"), self, activated=self.set_page_done)
        QShortcut(QKeySequence("Ctrl+l"), self, activated=self.open_logs_dir, context=Qt.ApplicationShortcut)
        QShortcut(QKeySequence("Ctrl+d"), self, activated=self.switch_debug_mode, context=Qt.ApplicationShortcut)

        self.forced_exit = False
        self.debug_mode = False

    # ui
    def init_ui(self):
        self.apply_style(self)
        try:
            prefs = app_dirs.get_global_config()
        except Exception as e:
            logger.exception(f"Failed to get preferences. {e}")
        else:
            install_path = prefs.get('install_path', app_dirs.install_dir())
            self.installation_path_le.setText(str(install_path))
            self.add_desktop_shortcut_cbx.setChecked(prefs.get('add_desktop_shortcut', True))
            self.add_menu_shortcut_cbx.setChecked(prefs.get('add_main_menu_shortcut', True))
        logger.info('Installer started....')

    def on_bundle_changed(self, bundle_name):
        self.custom_versions_te.setVisible(bundle_name == 'custom' and self.select_bundle_cbb.isVisible())
        if bundle_name not in ['custom', 'default']:
            packages = self.select_bundle_cbb.get_bundle(bundle_name)
            if packages:
                self.bundle_content_lb.setText('\n'.join(packages))
            else:
                self.bundle_content_lb.setText(f'No custom Packages in bundle {bundle_name}')
            self.bundle_content_lb.show()

        else:
            self.bundle_content_lb.hide()

    @classmethod
    def apply_style(cls, widget):
        style_file = Path(__file__).parent / "assets/style.css"
        if style_file.is_file():
            widget.setStyleSheet(style_file.read_text())

    def prepare_svg(self, svg_path: str, size: int = 64) -> QIcon:
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def closeEvent(self, event) -> None:
        if not self.forced_exit and not QMessageBox.question(self, "Cancel",
                "Cancel install and exit ?") == QMessageBox.Yes:
            event.ignore()
        else:
            super().closeEvent(event)

    # callbacks
    def on_click_next(self):
        self.set_page_settings()

    def on_click_cancel(self):
        if QMessageBox.question(self, "Cancel installation", "Exit ?") == QMessageBox.Yes:
            super().close()

    def on_click_install(self):
        self.start_installation_process(
            install_path=self.installation_path_le.text(),
            desktop_shortcut=self.add_desktop_shortcut_cbx.isChecked(),
            main_menu_shortcut=self.add_menu_shortcut_cbx.isChecked(),
        )
        self.set_page_logs()

    def on_click_browse(self):
        f = QFileDialog.getExistingDirectory(self, "Browse")
        if f:
            self.installation_path_le.setText(f)

    def on_click_back(self):
        self.set_page_settings()

    def on_click_cancel_install(self):
        if QMessageBox.question(self, "Cancel installation", "Stop install and exit ?") == QMessageBox.Yes:
            if self.proc is not None:
                if self.proc.isOpen():
                    self.proc.kill()
                    self.proc.waitForFinished(300)
                    self.output_logs.append('Canceled')
                    self.proc = None
            self.set_page_settings()

    def on_click_finish(self):
        self.forced_exit = True
        super().close()

    def on_process_output(self):
        output = self.proc.readAll()
        output = bytes(output).decode("utf-8", errors="ignore").strip()
        if output:
            self.output_logs.append(output)

    def on_process_finished(self, exit_code, status, error_text: str  = None):
        if exit_code == 0:
            self.set_page_done()
        else:
            if error_text:
                self.output_logs.append(error_text)
                QMessageBox.critical(self, "Error", error_text)
        self.proc = None
        self.output_logs.append('\n\n')

    # pages
    def set_page_welcome(self):
        self.label_welcome.setText('Welcome to the agio.desk Setup Wizard')
        self.book_widget.setCurrentIndex(0)

    def set_page_settings(self):
        self.label_welcome.setText('Select options and press Install')
        self.book_widget.setCurrentIndex(1)

    def set_page_logs(self):
        self.label_welcome.setText('Processing...')
        self.book_widget.setCurrentIndex(2)

    def set_page_done(self):
        self.label_welcome.setText('Installation completed!')
        self.book_widget.setCurrentIndex(3)

    # def set_page_update(self):
    #     self.label_welcome.setText('Update / Reinstall / Remove')
    #     self.book_widget.setCurrentIndex(4)

    def switch_debug_mode(self):
        if self.book_widget.currentIndex() == 1:
            self.debug_mode = not self.debug_mode
            self.update_bundle_selector()

    def update_bundle_selector(self):
        if self.debug_mode:
            try:
                self.select_bundle_cbb.reload()
                self.select_bundle_cbb.show()
                self.bundle_lb.show()
            except Exception as e:
                self.output_logs.append(str(e))
                QMessageBox.critical(self, "Error", str(e))
        else:
            self.select_bundle_cbb.hide()
            self.bundle_lb.hide()
            self.custom_versions_te.hide()
            self.bundle_content_lb.hide()

    def get_installation_version(self) -> dict:
        """
        [
        {'agio_core': {'ref_type': 'branch', 'value': 'dev', 'raw': 'agio_core:branch=dev'}}
        ...
        ]
        """
        bundle = self.select_bundle_cbb.currentText()
        if bundle:
            if bundle == 'default':
                return {}
            elif bundle == 'custom':
                code = self.custom_versions_te.toPlainText()
                values = customization.parse_custom_code(code)
                return values
            else:
                bundle_data = self.select_bundle_cbb.get_bundle(bundle)
                if not bundle_data:
                    raise Exception('Bundle "{}" not found'.format(bundle))
                values = customization.parse_custom_code('\n'.join(bundle_data))
                return values

    def open_logs_dir(self):
        log_dir = app_dirs.logs_dir()
        if log_dir.exists():
            open_path(log_dir)
        else:
            QMessageBox.critical(self, "Error", "Logs directory does not exist")


    # processing
    def start_installation_process(self, install_path, **kwargs):

        cmd = file_tools.get_executable()
        cmd.extend(['--install-path', install_path])
        if kwargs.get('desktop_shortcut'):
            cmd.append('--add-desktop-shortcut')
        if kwargs.get('main_menu_shortcut'):
            cmd.append('--add-main-menu-shortcut')
        custom_versions: dict = self.get_installation_version()
        if custom_versions:
            for k, v in custom_versions.items():
                cmd.extend(['--package-version', v['raw']])
        # start process
        msg = f'CMD: {" ".join(map(str, cmd))}'
        logger.info(msg)
        self.output_logs.clear()
        self.proc = QProcess()
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyRead.connect(self.on_process_output)
        self.proc.finished.connect(self.on_process_finished)
        self.output_logs.append(msg)
        self.proc.start(cmd[0], cmd[1:])
        if self.proc.error() == QProcess.ProcessError.FailedToStart:
            self.on_process_finished(1, None, self.proc.errorString())



class CheckBoxLabel(QLabel):
    def __init__(self, checkbox, *args, **kwargs):
        super(CheckBoxLabel, self).__init__(*args, **kwargs)
        self.checkbox = checkbox

    def mouseReleaseEvent(self, event):
        self.checkbox.setChecked(not self.checkbox.isChecked())
        return super().mouseReleaseEvent(event)


class BundleSelectorWidget(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setMaximumWidth(200)
        self.data = None

    def reload(self):
        bundle_list_url = 'https://storage.yandexcloud.net/agio-public/pipe-config/installer-bundles.json'
        text_data = requests.get(bundle_list_url).text
        self.data = json.loads(text_data)
        # Example:
        # {'installer_bundles':
        #   {'staging':
        #       ['agio_core:branch=dev', 'agio_pipe:tag=0.0.8'],
        #    'bundle-test':
        #       ['agio_core:tag=0.0.9', 'agio_pipe:branch=dev']
        #    }
        # }
        names = list(self.data.get('installer_bundles', []))
        self.clear()
        self.addItem('default')
        self.addItems(names)
        self.addItem('custom')


    def get_bundle_data(self):
        if self.data:
            current_name = self.currentText()
            if current_name == 'default':
                return
            bundle = self.data['installer_bundles'].get(current_name)
            return bundle

    def get_bundle(self, name):
        return self.data.get('installer_bundles', {}).get(name)



def center_on_screen(widget, app):
    cursor_pos: QPoint = QCursor.pos()
    current_screen: QScreen = app.screenAt(cursor_pos)
    if current_screen is None:
        current_screen = app.primaryScreen()
        if current_screen is None:
            logger.error("Screens not found")
            return
    screen_geometry = current_screen.availableGeometry()
    widget_geometry = widget.frameGeometry()
    widget_geometry.moveCenter(screen_geometry.center())
    widget.move(widget_geometry.topLeft())


def open_installer_dialog():
    app = QApplication(sys.argv)
    window = AgioDeskInstallerDialog()
    center_on_screen(window, app)
    window.show()
    sys.exit(app.exec())


def check_started_as_admin():
    if IS_WINDOWS:
        if not process_utils.is_started_as_admin():
            app = QApplication()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle('Admin required')
            msg.setText('Admin privileges required.')
            msg.setInformativeText('Restart installer as Admin to continue.')
            btn = msg.addButton('OK', QMessageBox.AcceptRole)
            msg.setDefaultButton(btn)
            AgioDeskInstallerDialog.apply_style(msg)
            msg.exec()
            sys.exit(app.quit())


if __name__ == '__main__':
    import click
    # agio-drive-setup --install-path ~/agio --add-shortcuts

    @click.command()
    @click.option("-i", "--install-path", type=str, required=False, default=None,
                  help="Path for installation")
    @click.option("-d", "--add-desktop-shortcut", is_flag=True, required=False, default=False,
                  help="Add a shortcut to desktop")
    @click.option("-m", "--add-main-menu-shortcut", is_flag=True, required=False, default=False,
                  help="Add a shortcut to Main Manu")
    @click.option("-c", "--custom-version-code", required=False,
                  help="Custom version in BASE64 encoded string")
    @click.option("-p", "--package-version", required=False, multiple=True,
                  help="Package version in format <package-name>:<ref-type>=<ref-value>")
    def install(install_path: str, add_desktop_shortcut: bool, add_main_menu_shortcut: bool,
                custom_version_code: str, package_version: list[str]|None) -> None:
        if not install_path:
            check_started_as_admin()
            open_installer_dialog()
        else:
            if IS_WINDOWS and not process_utils.is_started_as_admin():
                raise Exception('Admin privileges required. Restart installer as Admin to continue.')
            versions = None
            if custom_version_code and package_version:
                raise Exception('Custom version and package version are mutually exclusive')
            if custom_version_code:
                versions = customization.parse_custom_code(custom_version_code)
            elif package_version:
                versions = customization.parse_args(package_version) or None
            start_install(
                install_path=install_path,
                package_versions=versions,
                add_desktop_shortcut=add_desktop_shortcut,
                add_main_menu_shortcut=add_main_menu_shortcut,
            )

    install()