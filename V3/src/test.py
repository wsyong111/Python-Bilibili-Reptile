import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout


class MyWindow(QWidget):

	def __init__(self):  # self 就是一个实例对象
		super().__init__()  # 子类的方法调用父类的方法进行初始化

		self.setGeometry(300, 300, 250, 150)
		self.setWindowTitle('grid')
		self.show()

		self.layout_grid01()

	def layout_grid01(self):
		grid = QGridLayout()

		label1 = QWidget()
		label1.setStyleSheet("background-color:red; border: 0;")
		label1.setContentsMargins(0, 0, 0, 0)
		label1.setMaximumSize(100, 99999)
		label2 = QWidget()
		label2.setStyleSheet("background-color:green; border: 0;")
		label2.setContentsMargins(0, 0, 0, 0)

		grid.addWidget(label1, 0, 0)
		grid.addWidget(label2, 0, 1, 0, 2)
		grid.setContentsMargins(0, 0, 0, 0)

		self.setLayout(grid)


if __name__ == '__main__':
	app = QApplication(sys.argv)  # 创建一个应用对象
	window = MyWindow()  # 创建MyWindow实例
	window.show()  # 展示窗口
	sys.exit(app.exec_())  # 进入主程序循环 并安全退出
