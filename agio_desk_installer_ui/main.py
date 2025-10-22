import platform
import subprocess
import sys, os
from pathlib import Path
from PySide6.QtCore import *
from PySide6.QtCore import QSize, QProcess
from PySide6.QtGui import *
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget

from agio_desk_installer.main import main

IS_FROZEN =  '__compiled__' in globals()

class AgioDeskInstallerDialog(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        path_to_icon = os.path.join(os.path.dirname(__file__), "assets/icons/")
        self.default_install_path = str("куда его ставить ?")
        self.setWindowTitle("agio.desk Installer")
        icon = self.prepare_svg(path_to_icon + "favicon-o-knob-16.svg")
        self.setWindowIcon(icon)

        self.centralwidget = QWidget()

        self.central_ly = QVBoxLayout(self.centralwidget)

        self.top_widjet = QWidget(self.centralwidget)
        self.top_widjet.setMinimumSize(QSize(0, 100))
        # welcome text
        self.top_ly = QHBoxLayout(self.top_widjet)
        self.label_welcome = QLabel("Welcome to agio.desk installer")
        font = QFont()
        font.setPixelSize(14)
        font.setBold(True)
        self.label_welcome.setFont(font)
        self.top_ly.addWidget(self.label_welcome)
        # icon
        self.label_icon = QSvgWidget(path_to_icon + "logo.svg")
        self.label_icon.setFixedSize(QSize(200, 90))
        self.top_ly.addWidget(self.label_icon)

        self.central_ly.addWidget(self.top_widjet)
        self.line = QFrame(self.centralwidget)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.central_ly.addWidget(self.line)
        # book
        self.book_widget = QStackedWidget(self.centralwidget)
        # page1
        self.page_1 = QWidget()
        self.page1_ly = QVBoxLayout(self.page_1)

        self.label_step1 = QLabel("Welcome. Ready to install Agio.desk? Click Next to continue.")
        self.label_step1.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.page1_ly.addWidget(self.label_step1)

        self.page1_but = QHBoxLayout()
        self.page1_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.next = QPushButton("Next", clicked=self.click_next)
        self.page1_but.addWidget(self.next)
        self.page1_ly.addLayout(self.page1_but)
        self.page1_ly.setStretch(0, 1)
        self.book_widget.addWidget(self.page_1)

        # page2
        self.page_2 = QWidget()
        self.settings_ly = QVBoxLayout()
        self.page_2.setLayout(self.settings_ly)

        self.install_settings = QGroupBox('Settings')
        self.settings_ly.addWidget(self.install_settings)
        self.formLayout = QFormLayout(self.install_settings)
        self.install_settings.setLayout(self.formLayout)

        self.page2_but = QHBoxLayout()
        self.page2_but.setContentsMargins(0, 0, 0, 0)
        self.page2_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.cancel = QPushButton("Cancel", clicked=self.click_cancel)
        self.page2_but.addWidget(self.cancel)

        self.install = QPushButton("Install", clicked=self.click_install)
        self.page2_but.addWidget(self.install)
        self.settings_ly.addLayout(self.page2_but)

        self.browse_ly = QHBoxLayout()
        self.lineEdit = QLineEdit(self.install_settings)
        self.browse_ly.addWidget(self.lineEdit)
        self.toolButton = QPushButton("Browse...", clicked=self.click_browser)
        self.browse_ly.addWidget(self.toolButton)
        self.formLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.browse_ly)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, QLabel("Destination"))

        self.dsktp_check = QCheckBox('', checked=True)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.dsktp_check)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, QLabel("Add Desktop Shortcut"))

        self.menu_check = QCheckBox('', checked=True)
        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.menu_check)
        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, QLabel("Add Main Menu Shortcut"))

        self.book_widget.addWidget(self.page_2)


        # page3
        self.page_3 = QWidget()
        self.logs_ly = QHBoxLayout(self.page_3)
        self.logs_ly.setGeometry(QRect(0, 480, 811, 26))

        self.logs_but = QHBoxLayout()
        self.logs_but.setContentsMargins(0, 0, 0, 0)
        self.logs_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.back = QPushButton("Back", clicked=self.click_on_back)
        self.logs_but.addWidget(self.back)
        self.back.hide()
        self.cancel_3 = QPushButton("Cancel", clicked=self.click_cancel_install)
        self.logs_but.addWidget(self.cancel_3)
        self.logs_ly.addLayout(self.logs_but)

        self.groupBox = QGroupBox(self.page_3)
        self.groupBox.setGeometry(QRect(0, 20, 811, 451))
        self.progressbar_ly = QVBoxLayout(self.groupBox)
        # progressbar
        self.progressBar = QProgressBar(self.groupBox)
        self.progressBar.setValue(24)
        self.progressbar_ly.addWidget(self.progressBar)
        self.progressBar.hide()
        # output
        self.output_logs = QTextBrowser(self.groupBox)
        self.progressbar_ly.addWidget(self.output_logs)

        self.book_widget.addWidget(self.page_3)
        # page4
        self.page_4 = QWidget()
        self.last_ly = QWidget(self.page_4)
        self.last_ly.setGeometry(QRect(0, 480, 811, 26))

        self.fin_but = QHBoxLayout(self.last_ly)
        self.fin_but.setContentsMargins(0, 0, 0, 0)
        self.fin_but.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.doc_button = QPushButton("Open docs", clicked=self.click_open_docs)
        self.fin_but.addWidget(self.doc_button)
        self.back_2 = QPushButton("Finish", clicked=self.click_finish)
        self.fin_but.addWidget(self.back_2)

        self.widget = QWidget(self.page_4)
        self.widget.setGeometry(QRect(20, 30, 771, 421))
        self.finish_ly = QHBoxLayout(self.widget)
        self.finish_ly.setContentsMargins(0, 0, 0, 0)
        self.label_finish = QLabel("ICON")
        self.finish_ly.addWidget(self.label_finish)

        self.finish_check_ly = QVBoxLayout()
        self.finish_check_ly.setSpacing(6)
        self.finish_check_ly.setContentsMargins(-1, 0, -1, 0)
        self.label = QLabel("Install is done. Click on open docs for read documentation. Click open settings for set you template")

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QSize(16777215, 16777100))
        self.label.setBaseSize(QSize(0, 100))
        self.label.setAutoFillBackground(False)

        self.finish_check_ly.addWidget(self.label)

        self.checkBox_run_agio = QCheckBox(self.widget)
        self.checkBox_run_agio.setObjectName("run_agio")
        self.finish_check_ly.addWidget(self.checkBox_run_agio)

        self.checkBox_open_settings = QCheckBox(self.widget)
        self.checkBox_open_settings.setObjectName("open_settings")
        self.finish_check_ly.addWidget(self.checkBox_open_settings)
        self.finish_ly.addLayout(self.finish_check_ly)

        self.book_widget.addWidget(self.page_4)

        self.central_ly.addWidget(self.book_widget)

        self.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.set_page_welcome()
        self.resize(800, 500)
        self.init_ui()
        self.proc: QProcess = None

        QShortcut(QKeySequence("Alt+1"), self, activated=self.set_page_welcome)
        QShortcut(QKeySequence("Alt+2"), self, activated=self.set_page_settings)
        QShortcut(QKeySequence("Alt+3"), self, activated=self.set_page_logs)
        QShortcut(QKeySequence("Alt+4"), self, activated=self.set_page_done)
        self.forced_exit = False
        # if not self.is_admin():
        #     QMessageBox.warning(self, "Warning", "Please restart with admin privileges")
        #     QApplication.instance().quit()
        #     sys.exit(0)
        #     return

    def init_ui(self):
        self.apply_style()
        # self.lineEdit.setText(self.default_install_path)

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

    def click_next(self):
        self.set_page_settings()

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

    def click_cancel(self):
        if QMessageBox.question(self, "Cancel installation", "Exit ?") == QMessageBox.Yes:
            super().close()

    def click_install(self):
        # пока еще не понятно что тут будет как заглушка
        self.book_widget.setCurrentIndex(2)

    def click_browser(self):
        f = QFileDialog.getExistingDirectory(self, "Browse")
        if f:
            self.lineEdit.setText(f)

    def click_on_back(self):
        self.set_page_settings()

    def click_cancel_install(self):
        if QMessageBox.question(self, "Cancel installation", "Stop install and exit ?") == QMessageBox.Yes:
            if self.proc is not None:
                if self.proc.isOpen():
                    self.proc.kill()
                    self.proc.waitForFinished(300)
                    self.output_logs.append('Canceled')
                    self.proc = None
            self.set_page_settings()

    def click_open_docs(self):
        pass

    def click_finish(self):
        # if self.run_agio.isChecked():
        #     install_dir = self.line_path.text()
        #     system = platform.system()
        #     if system == "Windows":
        #         self.win_run(install_dir)
        #     elif system == "Linux":
        #         self.linux_run(install_dir)
        # self.forced_exit = True
        super().close()

    def is_admin(self) -> bool:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0

if __name__ == '__main__':
    import click
    # agio-drive-setup --install-dir ~/agio --add-shortcuts --clean
    @click.command()
    @click.option("-i", "--install-dir", type=str, required=False, default=None, help="dir for installation")
    @click.option("-a", "--add-shortcut", is_flag=True, required=False, default=True, help="add a shortcut in desktop")
    @click.option("-m", "--add-shortcut_in_settings", is_flag=True, required=False, default=False,
                  help="add a shortcut in settings")
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
        main(
            path_to_install=install_dir,
            add_shortcut=add_shortcut,
            add_shortcut_menu=add_shortcut_in_settings,
            autorun=autorun,
            open_docs=open_docs,
            open_settings=open_settings
        )
        # if any([install_dir, add_shortcut]):
            # non gui mode
            # main(path_to_install=install_dir, add_shortcut=add_shortcut, add_shortcut_menu=add_shortcut_in_settings, autorun=autorun, open_docs=open_docs, open_settings=open_settings)
        # else:
            # open dialog
        app = QApplication(sys.argv)
        window = AgioDeskInstallerDialog()
        window.show()
        sys.exit(app.exec())
    install()