import os

import uiComponents
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

from libs.utils import JsonReader, Translate

CHECK_FILES = [
	["./config.json", True],
	["./en-US", False],
	["./zh-CN", False],
	["./assets", False]
]

config = JsonReader("./config.json")


translateFile = Translate("./")
translateFile.lang = config.getValue("GuiSettings.Language")
translateFile.loadFile()


def main():
	app = QApplication([])

	ui = uiComponents.MainGui(translateFile, config, app)
	ui.show()

	sys.exit(app.exec())


if __name__ == "__main__":
	# 文件检查
	for item in CHECK_FILES:
		if os.path.exists(item[0]):
			continue

		if item[1]:
			if os.path.isfile(item[0]):
				continue
		else:
			if os.path.isdir(item[0]):
				continue

		QMessageBox.critical(None, "Error", f"Cannot find {'file' if item[1] else 'folder'} {item[0]}")
		sys.exit(-1)

	main()
