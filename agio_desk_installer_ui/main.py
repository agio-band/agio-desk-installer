from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QStatusBar, QTextBrowser,
    QToolButton, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(833, 662)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.top_widdjet = QWidget(self.centralwidget)
        self.top_widdjet.setObjectName(u"top_widdjet")
        self.top_widdjet.setMinimumSize(QSize(0, 100))
        self.horizontalLayout = QHBoxLayout(self.top_widdjet)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_welcome = QLabel(self.top_widdjet)
        self.label_welcome.setObjectName(u"label_welcome")

        self.horizontalLayout.addWidget(self.label_welcome)

        self.label_icon = QLabel(self.top_widdjet)
        self.label_icon.setObjectName(u"label_icon")

        self.horizontalLayout.addWidget(self.label_icon)


        self.verticalLayout.addWidget(self.top_widdjet)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.book_wodjet = QStackedWidget(self.centralwidget)
        self.book_wodjet.setObjectName(u"book_wodjet")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.verticalLayout_2 = QVBoxLayout(self.page_1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_step1 = QLabel(self.page_1)
        self.label_step1.setObjectName(u"label_step1")
        self.label_step1.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_2.addWidget(self.label_step1)

        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.button_layout.addItem(self.horizontalSpacer)

        self.next = QPushButton(self.page_1)
        self.next.setObjectName(u"next")

        self.button_layout.addWidget(self.next)


        self.verticalLayout_2.addLayout(self.button_layout)

        self.verticalLayout_2.setStretch(0, 1)
        self.book_wodjet.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.horizontalLayoutWidget = QWidget(self.page_2)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 470, 801, 31))
        self.buutton_layout = QHBoxLayout(self.horizontalLayoutWidget)
        self.buutton_layout.setObjectName(u"buutton_layout")
        self.buutton_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buutton_layout.addItem(self.horizontalSpacer_2)

        self.cancel = QPushButton(self.horizontalLayoutWidget)
        self.cancel.setObjectName(u"cancel")

        self.buutton_layout.addWidget(self.cancel)

        self.install = QPushButton(self.horizontalLayoutWidget)
        self.install.setObjectName(u"install")

        self.buutton_layout.addWidget(self.install)

        self.instal_settings = QGroupBox(self.page_2)
        self.instal_settings.setObjectName(u"instal_settings")
        self.instal_settings.setGeometry(QRect(10, 30, 791, 381))
        self.formLayout = QFormLayout(self.instal_settings)
        self.formLayout.setObjectName(u"formLayout")
        self.checkBox_1 = QCheckBox(self.instal_settings)
        self.checkBox_1.setObjectName(u"checkBox_1")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.checkBox_1)

        self.checkBox_2 = QCheckBox(self.instal_settings)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.checkBox_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEdit = QLineEdit(self.instal_settings)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_2.addWidget(self.lineEdit)

        self.toolButton = QToolButton(self.instal_settings)
        self.toolButton.setObjectName(u"toolButton")

        self.horizontalLayout_2.addWidget(self.toolButton)


        self.formLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.label_browse = QLabel(self.instal_settings)
        self.label_browse.setObjectName(u"label_browse")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_browse)

        self.book_wodjet.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.horizontalLayoutWidget_3 = QWidget(self.page_3)
        self.horizontalLayoutWidget_3.setObjectName(u"horizontalLayoutWidget_3")
        self.horizontalLayoutWidget_3.setGeometry(QRect(0, 480, 811, 26))
        self.button_layout_2 = QHBoxLayout(self.horizontalLayoutWidget_3)
        self.button_layout_2.setObjectName(u"button_layout_2")
        self.button_layout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.button_layout_2.addItem(self.horizontalSpacer_3)

        self.back = QPushButton(self.horizontalLayoutWidget_3)
        self.back.setObjectName(u"back")

        self.button_layout_2.addWidget(self.back)

        self.groupBox = QGroupBox(self.page_3)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 20, 811, 451))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.progressBar = QProgressBar(self.groupBox)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.verticalLayout_3.addWidget(self.progressBar)

        self.textBrowser = QTextBrowser(self.groupBox)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout_3.addWidget(self.textBrowser)

        self.book_wodjet.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.horizontalLayoutWidget_4 = QWidget(self.page_4)
        self.horizontalLayoutWidget_4.setObjectName(u"horizontalLayoutWidget_4")
        self.horizontalLayoutWidget_4.setGeometry(QRect(0, 480, 811, 26))
        self.button_layout_3 = QHBoxLayout(self.horizontalLayoutWidget_4)
        self.button_layout_3.setObjectName(u"button_layout_3")
        self.button_layout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.button_layout_3.addItem(self.horizontalSpacer_4)

        self.doc_button = QPushButton(self.horizontalLayoutWidget_4)
        self.doc_button.setObjectName(u"doc_button")

        self.button_layout_3.addWidget(self.doc_button)

        self.back_2 = QPushButton(self.horizontalLayoutWidget_4)
        self.back_2.setObjectName(u"back_2")

        self.button_layout_3.addWidget(self.back_2)

        self.widget = QWidget(self.page_4)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(20, 30, 771, 421))
        self.horizontalLayout_3 = QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_finish = QLabel(self.widget)
        self.label_finish.setObjectName(u"label_finish")

        self.horizontalLayout_3.addWidget(self.label_finish)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, 0, -1, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QSize(16777215, 16777100))
        self.label.setBaseSize(QSize(0, 100))
        self.label.setAutoFillBackground(False)

        self.verticalLayout_4.addWidget(self.label)

        self.checkBox_run_agio = QCheckBox(self.widget)
        self.checkBox_run_agio.setObjectName(u"checkBox_run_agio")
        self.checkBox_run_agio.setCheckable(False)
        self.checkBox_run_agio.setAutoRepeat(False)

        self.verticalLayout_4.addWidget(self.checkBox_run_agio)

        self.checkBox_open_settings = QCheckBox(self.widget)
        self.checkBox_open_settings.setObjectName(u"checkBox_open_settings")

        self.verticalLayout_4.addWidget(self.checkBox_open_settings)


        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.book_wodjet.addWidget(self.page_4)

        self.verticalLayout.addWidget(self.book_wodjet)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.book_wodjet.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_welcome.setText(QCoreApplication.translate("MainWindow", u"Welcome", None))
        self.label_icon.setText(QCoreApplication.translate("MainWindow", u"  ICON", None))
        self.label_step1.setText(QCoreApplication.translate("MainWindow", u"Step 1", None))
        self.next.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.cancel.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.install.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.instal_settings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.checkBox_1.setText(QCoreApplication.translate("MainWindow", u"create_shortcut", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"create_shrotcut_in_menu", None))
        self.toolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_browse.setText(QCoreApplication.translate("MainWindow", u"destanation", None))
        self.back.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"logs", None))
        self.doc_button.setText(QCoreApplication.translate("MainWindow", u"view_doc", None))
        self.back_2.setText(QCoreApplication.translate("MainWindow", u"finish", None))
        self.label_finish.setText(QCoreApplication.translate("MainWindow", u"ICON", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Complete", None))
        self.checkBox_run_agio.setText(QCoreApplication.translate("MainWindow", u"run_agio.desk", None))
        self.checkBox_open_settings.setText(QCoreApplication.translate("MainWindow", u"open_settings", None))
    # retranslateUi

