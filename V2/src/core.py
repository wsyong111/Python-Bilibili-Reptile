"""
!! 此文件暗藏玄只因 !!

此只因文件遵循 PEP8 语法编写
"""


import threading
import time

from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.traceback import install as TracebackRunner

import MainModules.article as Article
import MainModules.download as DownloadModule
import MainModules.utils as functions
import MainModules.uplive as UpLive

TracebackRunner()

console = Console()

CONFIG_FILE_PATH = "./settings.json"

config = {}

runningReptileThreads = []
imageUrls = []
getImageCount_Live = 0
usedTime_Live = 0
getImageCount_Article = 0
usedTime_Article = 0

sendRequestsArticle = 0
sendRequestsLive = 0


def readConfig() -> None:
	"""
	读取配置文件
	"""

	global config

	config = functions.readJsonFile(CONFIG_FILE_PATH)


def clearStoppedThread() -> None:
	"""
	清理掉 runningReptileThreads 内所有停止的线程
	"""

	for thread in runningReptileThreads:
		if not thread.is_alive():
			del runningReptileThreads[runningReptileThreads.index(thread)]


def formatTime(sec) -> str:
	"""
	将秒转换成 HH:MM:SS

	:param sec:
	:return:
	"""

	minute, second = divmod(sec, 60)
	hour, minute = divmod(minute, 60)

	return "%02d:%02d:%02d" % (hour, minute, second)


def articleThread(userIDList, progressBar, mainTask):
	"""
	Up主文章图片爬取线程

	:param userIDList: Up主ID列表
	:param progressBar: 进度条
	:param mainTask: 进度条ID
	"""

	global imageUrls, sendRequestsArticle, usedTime_Article, getImageCount_Article

	startTime = time.time()
	imageUrls_, sendRequests = Article.onLoad(userIDList, progressBar)
	usedTime_Article = time.time() - startTime

	imageUrls += imageUrls_
	getImageCount_Article = len(imageUrls_)
	sendRequestsArticle = sendRequests

	for v in imageUrls_:
		getImageCount_Article = len(v)

	progressBar.advance(mainTask)


def upLiveThread(userIDList, progressBar, mainTask):
	"""
	Up主动态图片爬取线程

	:param userIDList: Up主ID列表
	:param progressBar: 进度条
	:param mainTask: 进度条ID
	"""

	global imageUrls, sendRequestsLive, usedTime_Live, getImageCount_Live

	startTime = time.time()
	imageUrls_, sendRequests = UpLive.onLoad(userIDList, progressBar)
	usedTime_Live = time.time() - startTime

	imageUrls += imageUrls_
	getImageCount_Live = len(imageUrls_)
	sendRequestsLive = sendRequests

	for v in imageUrls_:
		getImageCount_Article = len(v)

	progressBar.advance(mainTask)


def runReptileThreads(progressBar, mainTask):
	"""
	爬虫主线程
	"""

	NEED_LOAD_THREADS = [
		articleThread,
		upLiveThread
	]

	for needLoadThread in NEED_LOAD_THREADS:
		thread = threading.Thread(
			target=needLoadThread,
			args=(config["ReptileSettings"]["UserList"], progressBar, mainTask)
		)
		thread.setDaemon(True)
		thread.start()

		runningReptileThreads.append(thread)

	while len(runningReptileThreads) > 0:
		clearStoppedThread()

		time.sleep(0.1)


def main():
	global imageUrls

	with Progress() as progressBar:
		mainTask = progressBar.add_task(description="进度: 未知", total=6)

		# 读取配置文件 开始
		progressBar.update(mainTask, description="进度: 读取设置")
		progressBar.log("[green]\\[Log] 正在读取设置...")
		readConfig()
		progressBar.log("[green]\\[Log] ... 完成")
		progressBar.advance(mainTask)
		progressBar.update(mainTask, description="进度: 读取完成")
		# 读取配置文件 结束

		# 爬虫代码 开始
		progressBar.update(mainTask, description="进度: 正在爬取")
		runReptileThreads(progressBar, mainTask)
		progressBar.update(mainTask, description="进度: 爬取完成")
		progressBar.advance(mainTask)
		# 爬虫代码 结束

		# 下载文件 开始
		progressBar.update(mainTask, description="进度: 正在下载")

		imageUrls = list(set(imageUrls))

		DownloadModule.download(imageUrls, path=config["ReptileSettings"]["OutputFolder"], progressBar=progressBar)
		progressBar.advance(mainTask)
		progressBar.update(mainTask, description="进度: 下载完成")
		# 下载文件 结束

		progressBar.update(mainTask, description="进度: 正在生成报告")
		progressBar.log("[green]\\[Log] 正在生成报告")
		reportTable = Table(
			show_header=True
		)

		reportTable.add_column("功能名字")
		reportTable.add_column("发送请求次数")
		reportTable.add_column("获得图片")
		reportTable.add_column("耗时")

		reportTable.add_row(
			"动态爬虫",
			f"[yellow]{sendRequestsLive}",
			f"[yellow]{getImageCount_Live}",
			f"[green]{formatTime(usedTime_Live)}"
		)

		reportTable.add_row(
			"文章爬虫",
			f"[yellow]{sendRequestsArticle}",
			f"[yellow]{getImageCount_Article}",
			f"[green]{formatTime(usedTime_Article)}"
		)

		reportTable.add_row(
			"[blue]总共",
			f"[yellow]{sendRequestsArticle + sendRequestsLive}",
			f"[yellow]{getImageCount_Article + getImageCount_Live}",
			f"[green]{formatTime(usedTime_Article + usedTime_Live)}"
		)

		progressBar.update(mainTask, description="进度: 生成完成")
		progressBar.remove_task(mainTask)
		progressBar.print(reportTable, justify="center")

	console.log("[green]\\[Log] 程序运行完成")

	return 0
