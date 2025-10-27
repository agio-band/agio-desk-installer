import json
import platform
import subprocess
import sys, os
import traceback
from pathlib import Path
from PySide6.QtCore import *
from PySide6.QtCore import QSize, QProcess
from PySide6.QtGui import *
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget

from agio_desk_installer.install_tools import start_install, customization

IS_FROZEN =  '__compiled__' in globals()

ONLINE_DOCS_URL = 'https://doki.agio.services/home'
WELCOME_TEXT = "Welcome. Ready to install Agio.desk? Click Next to continue."
THANKS_TEXT = f'''
Thank you for installing agio.desk.
<br>
<br>
For comprehensive guidance and detailed features, please consult the <a href="{ONLINE_DOCS_URL}">Online Documentation</a>.
<br>
We hope you enjoy using the program.
'''
ICONS_PATH = os.path.join(os.path.dirname(__file__), "assets/icons")


def get_default_install_path():
    return os.path.expanduser('~/agio/agio-desk')


class AgioDeskInstallerDialog(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.setWindowTitle("agio.desk Installer")
        icon = self.prepare_svg(os.path.join(ICONS_PATH, "favicon-o-knob-16.svg"))
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
        self.label_welcome = QLabel("Welcome to agio.desk installer")
        font = QFont()
        font.setPixelSize(14)
        font.setBold(True)
        self.label_welcome.setFont(font)
        self.top_ly.addWidget(self.label_welcome)
        # icon
        self.label_icon = QSvgWidget(os.path.join(ICONS_PATH, "logo.svg"))
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

        self.custom_versions_lb = QLabel()
        self.custom_versions_lb.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.page1_ly.addWidget(self.custom_versions_lb)

        self.page1_but = QHBoxLayout()
        self.page1_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.next = QPushButton("Next", clicked=self.on_click_next)
        self.page1_but.addWidget(self.next)
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
        self.installation_dir_le = QLineEdit()
        self.installation_dir_le.setPlaceholderText("Installation Path")
        self.installation_dir_le.setText(get_default_install_path())
        self.browse_ly.addWidget(self.installation_dir_le)
        self.toolButton = QPushButton("Browse...", clicked=self.on_click_browse)
        self.browse_ly.addWidget(self.toolButton)

        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.browse_ly)
        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, QLabel("Destination"))

        self.add_desktop_shortcut_cbx = QCheckBox('', checked=True)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.add_desktop_shortcut_cbx)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, QLabel("Add Desktop Shortcut"))

        self.add_menu_shortcut_cbx = QCheckBox('', checked=True)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.add_menu_shortcut_cbx)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, QLabel("Add Main Menu Shortcut"))

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
        self.thanks_lb.setText(THANKS_TEXT)
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

        # page 5
        # self.page_5 = QWidget()
        # self.update_ly = QVBoxLayout(self.page_4)
        # self.update_ly.setContentsMargins(30, 20, 30, 20)
        # self.page_5.setLayout(self.update_ly)
        # self.book_widget.addWidget(self.page_5)

        # other
        self.central_ly.addWidget(self.book_widget)

        self.setCentralWidget(self.centralwidget)

        self.set_page_welcome()
        self.resize(800, 500)
        self.init_ui()

        self.custom_versions = {}
        self.proc: QProcess|None = None

        # debug shortcuts
        QShortcut(QKeySequence("Alt+1"), self, activated=self.set_page_welcome)
        QShortcut(QKeySequence("Alt+2"), self, activated=self.set_page_settings)
        QShortcut(QKeySequence("Alt+3"), self, activated=self.set_page_logs)
        QShortcut(QKeySequence("Alt+4"), self, activated=self.set_page_done)
        # QShortcut(QKeySequence("Alt+5"), self, activated=self.set_page_update)
        QShortcut(QKeySequence("Ctrl+v"), self, activated=self.read_custom_versions)
        QShortcut(QKeySequence("Ctrl+r"), self, activated=self.reset_custom_versions)

        self.forced_exit = False
    # ui
    def init_ui(self):
        self.apply_style()

    def apply_style(self):
        style_file = Path(__file__).parent / "assets/style.css"
        if style_file.is_file():
            self.setStyleSheet(style_file.read_text())

    def prepare_svg(self, svg_path: str, size: int = 64) -> QIcon:
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    # callbacks
    def on_click_next(self):
        self.set_page_settings()

    def on_click_cancel(self):
        if QMessageBox.question(self, "Cancel installation", "Exit ?") == QMessageBox.Yes:
            super().close()

    def on_click_install(self):
        self.start_installation_process(
            install_dir=self.installation_dir_le.text(),
            desktop_shortcut=self.add_desktop_shortcut_cbx.isChecked(),
            main_menu_shortcut=self.add_menu_shortcut_cbx.isChecked(),
            versions_code=self.custom_versions.get('code')
        )
        self.set_page_logs()

    def on_click_browse(self):
        f = QFileDialog.getExistingDirectory(self, "Browse")
        if f:
            self.installation_dir_le.setText(f)

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
        # if self.run_agio.isChecked():
        #     install_dir = self.line_path.text()
        #     system = platform.system()
        #     if system == "Windows":
        #         self.win_run(install_dir)
        #     elif system == "Linux":
        #         self.linux_run(install_dir)
        # self.forced_exit = True
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
        self.label_welcome.setText('Welcome to agio.desk installer')
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

    # utils
    def read_custom_versions(self):
        if self.book_widget.currentIndex() != 0:
            return
        clipboard = QApplication.clipboard()
        code = clipboard.text()
        try:
            values = customization.parse_custom_code(code)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Could not parse clipboard: {e}")
            self.reset_custom_versions()
            return
        if values:
            self.custom_versions = {'code': code, 'values': values}
            self.update_custom_versions_label()

    def update_custom_versions_label(self):
        if self.custom_versions:
            text = ''
            for k, v in self.custom_versions['values'].items():
                text += f'{k}@{v['value']}<br>'
            html = (f"<html><head/><body>{text}<br>"
                    f"<i style=\" font-style:italic; color:#707070;\">(Ctrl+R to reset)</i></body></html>")
            self.custom_versions_lb.setText(html)
        else:
            self.custom_versions_lb.setText('')

    def reset_custom_versions(self):
        self.custom_versions = {}
        self.update_custom_versions_label()

    # processing
    def start_installation_process(self, install_dir, **kwargs):
        if IS_FROZEN:
            cmd = [sys.executable]
        else:
            cmd = [sys.executable, Path(__file__).resolve().as_posix()]
        cmd.extend(['--install-dir', install_dir])
        if kwargs.get('desktop_shortcut'):
            cmd.append('--add-desktop-shortcut')
        if kwargs.get('main_menu_shortcut'):
            cmd.append('--add-main-menu-shortcut')
        if self.custom_versions:
            for k, v in self.custom_versions['values'].items():
                cmd.extend(['--package-version', v['raw']])
        # start process
        self.proc = QProcess()
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyRead.connect(self.on_process_output)
        self.proc.finished.connect(self.on_process_finished)

        self.output_logs.append(f'CMD: {" ".join(map(str, cmd))}')
        self.proc.start(cmd[0], cmd[1:])
        if self.proc.error() == QProcess.ProcessError.FailedToStart:
            self.on_process_finished(1, None, self.proc.errorString())


def center_on_screen(widget, app):
    cursor_pos: QPoint = QCursor.pos()
    current_screen: QScreen = app.screenAt(cursor_pos)
    if current_screen is None:
        current_screen = app.primaryScreen()
        if current_screen is None:
            print("Screens not found")
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


if __name__ == '__main__':
    import click
    # agio-drive-setup --install-dir ~/agio --add-shortcuts

    @click.command()
    @click.option("-i", "--install-dir", type=str, required=False, default=None,
                  help="Path for installation")
    @click.option("-d", "--add-desktop-shortcut", is_flag=True, required=False, default=True,
                  help="Add a shortcut to desktop")
    @click.option("-m", "--add-main-menu-shortcut", is_flag=True, required=False, default=True,
                  help="Add a shortcut to Main Manu")
    @click.option("-c", "--custom-version-code", required=False,
                  help="Custom version in BASE64 encoded string")
    @click.option("-p", "--package-version", required=False, multiple=True,
                  help="Package version in format <package-name>:<ref-type>=<ref-value>")
    def install(install_dir: str, add_desktop_shortcut: bool, add_main_menu_shortcut: bool,
                custom_version_code: str, package_version: list[str]|None) -> None:
        if not install_dir:
            open_installer_dialog()
        else:
            versions = None
            if custom_version_code and package_version:
                raise Exception('Custom version and package version are mutually exclusive')
            if custom_version_code:
                versions = customization.parse_custom_code(custom_version_code)
            elif package_version:
                versions = customization.parse_args(package_version) or None
            start_install(
                path_to_install=install_dir,
                add_desktop_shortcut=add_desktop_shortcut,
                add_main_menu_shortcut=add_main_menu_shortcut,
                package_versions=versions
            )

    install()