"""
//(i0|i1)\.hdslb\.com/bfs/article/(.*)\.(png|jpg|webp)
"""

import atexit
import os
import random
import shutil
import string
import threading
import time

from fake_useragent import UserAgent
from rich.console import Console
from rich.table import Table

import Download
import article
import uplive

ImageOutputFolder = ".\\Output\\"

UserIdList = [ # 在此输入要被爬图的B站主播的UID
	"288472563",
	"51795981",
	"1100224942",
	"206895693",
	"382021859",
	"23091718",
	"1975289269",
	"2049825808",
	"1723817817",
	"478079553",
	"622197777"
]

RandomUserAgent = UserAgent()

Console = Console()

ImageUrlList = []
GetApi = 0
GetImage = 0

UpLiveStop = False
UpArticleStop = False

def TestPath(Path, AutoCreate=True):
	if not os.path.exists(Path):
		os.makedirs(Path)

def RandomText(Size=20):
	return "".join(random.sample(string.ascii_letters, Size))

def NewTempFolder(Path):
	Name = Path + "Temp{" + RandomText() + "}\\"

	os.mkdir(Name)

	return Name

def ReAllFile(Path):
	for File in os.listdir(Path):
		os.rename(Path + File, Path + RandomText() + os.path.splitext(File)[-1])

	time.sleep(3)

	Index = 0
	for File in os.listdir(Path):
		Name = str(Index) + os.path.splitext(File)[-1]
		if Name != File:
			os.rename(Path + File, Path + Name)
		Index += 1

def UpLiveThread():
	global ImageUrlList, UpLiveStop

	UpLiveStop = False

	Console.log("正在爬取动态")
	ImageUrlList_, GetImage_, GetApi_ = uplive.Load(UserIdList)

	ImageUrlList += ImageUrlList_
	GetApi = GetApi_
	GetImage = GetImage_

	Console.log("完成")

	UpLiveStop = True

def UpArticleThread():
	global ImageUrlList, UpArticleStop

	UpArticleStop = False

	Console.log("正在爬取专栏")
	ImageUrlList_, GetImage_, GetApi_ = article.Load(UserIdList)

	ImageUrlList += ImageUrlList_
	GetApi = GetApi_
	GetImage = GetImage_

	Console.log("完成")

	UpArticleStop = True

def StartMainThread():
	UpLiveThreadMain = threading.Thread(target=UpLiveThread)
	UpLiveThreadMain.setDaemon(True)
	UpLiveThreadMain.start()

	time.sleep(1)

	UpArticleThreadMain = threading.Thread(target=UpArticleThread)
	UpArticleThreadMain.setDaemon(True)
	UpArticleThreadMain.start()

	while UpArticleStop == False and UpLiveStop == False:
		Console.log()

		time.sleep(1)

def Main(TempFolder):
	for Folder in os.listdir(ImageOutputFolder):
		if ImageOutputFolder + Folder + "\\" != TempFolder:
			shutil.rmtree(ImageOutputFolder + Folder)

	StartMainThread()

	Console.log("正在下载文件...")
	Download.download.downloadFileList(ImageUrlList, Path=TempFolder, MaxRetries=100, Multithreading=True, MaxThreadSize=16)

	#----------------------------------------------------------------

	FileList = []
	NumberOfImageList = {}

	Console.log("正在分类文件中...")
	for File in os.listdir(TempFolder):
		FileSuffix = os.path.splitext(File)[-1]

		OutputFileName = ImageOutputFolder + FileSuffix[1:].lower() + "\\"

		if not os.path.exists(OutputFileName):
			os.mkdir(OutputFileName)
			NumberOfImageList[FileSuffix[1:].lower()] = 1

			FileList.append(OutputFileName)

		NumberOfImageList[FileSuffix[1:].lower()] += 1

		shutil.move(TempFolder + File, OutputFileName)

	Console.log("重命名文件...")
	for Folder in FileList:
		ReAllFile(Folder)

	OutputTable = Table(show_header=True)
	OutputTable.add_column("名字")
	OutputTable.add_column("数值")
	OutputTable.add_row("请求数量", "[orange]" + str(GetApi))
	for Index, Value in NumberOfImageList.items():
		OutputTable.add_row(Index + "图片", "[orange]" + str(Value))

	OutputTable.add_row("总共获得图片", "[orange]" + str(GetImage))

	Console.print(OutputTable)

if __name__ == "__main__":
	TempFolder = NewTempFolder(ImageOutputFolder)

	@atexit.register
	def clean():
		Console.log("正在清理缓存...")

		if os.path.exists(TempFolder):
			shutil.rmtree(TempFolder)

		Console.log("完成")

	Main(TempFolder)
