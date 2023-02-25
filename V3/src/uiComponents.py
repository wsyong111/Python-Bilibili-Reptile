import ctypes

import winsound
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from libs.utils import PathObject, Translate, JsonReader

GUI_ICON = PathObject("./assets/icon.ico")
GUI_DOWNLOAD_ICON = PathObject("./assets/download.png")

GUI_SIZE = QVector2D(500, 300)
GUI_BACKGROUND_COLOR = QColor(77, 77, 77)

GUI_FONT = QFont("Microsoft Yahei")


class MainGui(QMainWindow):
	tabIndex: int = 0

	def __init__(self, translate: Translate, configFile: JsonReader, app: QApplication, parent=None):
		super(MainGui, self).__init__(parent)

		self.translate: Translate = translate
		self.config = configFile
		self.app = app

		self.initUI()

	def addTab(self, Name: str):
		tabIndex = self.tabIndex
		self.tabIndex += 1

		selectButton = QPushButton(Name)
		self.sidebarList.addWidget(selectButton)

		tab = QWidget()

		self.content.addTab(tab, Name)

		def click(e):
			self.content.setCurrentIndex(tabIndex)

		selectButton.clicked.connect(click)

		return tab

	def initUI(self):
		self.setWindowTitle(self.translate["WindowTitle"])
		self.setWindowIcon(QIcon(GUI_ICON))
		self.resize(int(GUI_SIZE.x()), int(GUI_SIZE.y()))
		self.setMinimumSize(int(GUI_SIZE.x()), int(GUI_SIZE.y()))
		# self.setMaximumSize(int(GUI_SIZE.x()), int(GUI_SIZE.y()))
		self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")  # 设定任务栏图标

		# 设定托盘图标
		self.tray = QSystemTrayIcon()
		self.tray.hide()
		self.tray.setIcon(QIcon(GUI_ICON))
		self.tray.activated.connect(self.showGui)

		# 添加顶部栏
		self.topBar = self.menuBar()
		self.topBar_File = self.topBar.addMenu(self.translate["File"])

		self.topBar_File_OpenDownloadFolder = QAction(QIcon(GUI_DOWNLOAD_ICON), self.translate["OpenDownloadFolder"])
		self.topBar_File.addAction(self.topBar_File_OpenDownloadFolder)

		# 基本控件
		self.base = QWidget()
		self.base.setContentsMargins(0, 0, 0, 0)
		self.base.setObjectName("body")
		self.base.setContentsMargins(0, 0, 0, 0)
		self.setCentralWidget(self.base)

		# 添加部件
		self.sidebar = QWidget()
		self.sidebar.setContentsMargins(0, 0, 0, 0)
		self.sidebar.setMaximumSize(130, 16777215)
		self.sidebar.setContentsMargins(0, 0, 0, 0)
		self.sidebar.setObjectName("sidebar")

		self.content = QTabWidget()
		self.content.setContentsMargins(0, 0, 0, 0)
		self.content.setDocumentMode(True)
		self.content.setObjectName("content")

		gridLayout = QGridLayout()
		gridLayout.setContentsMargins(0, 0, 0, 0)
		gridLayout.setSpacing(0)
		gridLayout.addWidget(self.sidebar, 0, 0, 0, 1)
		gridLayout.addWidget(self.content, 0, 1, 0, 2)
		self.base.setLayout(gridLayout)

		self.sidebarList = QVBoxLayout()
		self.sidebarList.setContentsMargins(0, 0, 0, 0)
		self.sidebarList.setSpacing(0)
		self.sidebarList.setAlignment(Qt.AlignTop)
		self.sidebar.setLayout(self.sidebarList)

		for i in ["首页", "爬虫设置", "界面设置"]:
			w = self.addTab(i)

		# 加载设置
		self.loadSettings()

	def loadSettings(self):
		textColor = self.config.getValue("GuiSettings.FontColor")
		backgroundColor = self.config.getValue("GuiSettings.BackgroundColor")
		sidebarColor = self.config.getValue("GuiSettings.SidebarColor")
		buttonColor = self.config.getValue("GuiSettings.ButtonColor")

		self.setStyleSheet(f"""
			#body {{
				background: rgb({backgroundColor[0]}, {backgroundColor[1]}, {backgroundColor[2]});
			}}
			
			#sidebar {{
				background: rgb({sidebarColor[0]}, {sidebarColor[1]}, {sidebarColor[2]});
			}}
			
			#sidebar QPushButton {{
				width: 100%;
				height: 20px;
				color: rgb({textColor[0]}, {textColor[1]}, {textColor[2]});
				background: rgb({buttonColor[0]}, {buttonColor[1]}, {buttonColor[2]});
				text-align: left;
				padding: 4px;
				font-size: 14px;
				border: 0;
			}}
			
			#sidebar QPushButton:hover {{
				background: rgb({buttonColor[0] + 15}, {buttonColor[1] + 15}, {buttonColor[2] + 15});
			}}
			
			#content QTabBar::tab {{
				width: 0;
				height: 0;
				margin: 0;
				padding: 0;
				border: 0;
			}}
			
			#content QWidget {{
				border: 0;
				background: rgb({backgroundColor[0]}, {backgroundColor[1]}, {backgroundColor[2]});
			}}
			
			QMenuBar {{
				background: rgb({backgroundColor[0]}, {backgroundColor[1]}, {backgroundColor[2]});
				color: rgb({textColor[0]}, {textColor[1]}, {textColor[2]});
				border-bottom: 1px solid #000;
			}}
			
			QMenuBar {{
				background: rgb({backgroundColor[0]}, {backgroundColor[1]}, {backgroundColor[2]});
				color: rgb({textColor[0]}, {textColor[1]}, {textColor[2]});
				border-bottom: 1px solid #000;
			}}
			
			QMenuBar::item::hover {{
				background: #000;
			}}
		""")

	def showGui(self):
		self.tray.hide()
		self.show()

	def zoomToTray(self):
		self.tray.show()
		self.hide()

	def closeEvent(self, event: QCloseEvent):
		winsound.MessageBeep()

		userSelect = QMessageBox.question(
			self,
			self.translate["CloseMessageTitle"],
			self.translate["CloseMessage"],
			QMessageBox.Cancel | QMessageBox.Yes | QMessageBox.No,
			QMessageBox.No
		)

		if userSelect == QMessageBox.Yes:
			event.ignore()

			self.zoomToTray()
		elif userSelect == QMessageBox.No:
			event.accept()

		elif userSelect == QMessageBox.Cancel:
			event.ignore()
