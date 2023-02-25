import os
import threading
import time
from urllib.parse import unquote

import requests
from rich.progress import Progress

from . import errors

ProgressNumber = 0

def getFileName(URL: str) -> str or None:
	"""
	获取文件名

	通过URL获取文件名

	:param URL: 文件URL
	:return: 文件名
	"""

	FileName = ""
	HttpObject = getHead(URL)

	if HttpObject.status_code == requests.codes.ok:
		HttpHead = HttpObject.headers

		if "Content-Disposition" in HttpHead and HttpHead["Content-Disposition"]:
			ContentDisposition = HttpHead["Content-Disposition"]

			SplitContent = ContentDisposition.split(";")

			if len(SplitContent) > 1:
				if SplitContent[1].strip().lower().startswith("filename="):
					FileName = SplitContent[1].split("=")

					if len(FileName) > 1:
						FileName = unquote(FileName)

		if not FileName and os.path.basename(URL):
			FileName = os.path.basename(URL).split("?")[0]

		if not FileName:
			return None

		return FileName
	else:
		return None

def newFileName(Path=".\\", FileSuffix="") -> str:
	"""
	获取和给定路径内的文件不冲突的文件名

	:param Path: 文件夹路径
	:param FileSuffix: 文件后缀
	:return: 未被占用的文件名 (不含后缀)
	"""
	Count = 0

	while True:
		if not os.path.exists(Path + str(Count) + FileSuffix):
			return str(Count)

		Count += 1

def byteFormat(Byte: int, Precision=3) -> int and str:
	"""
	对文件大小进行格式化

	:param Byte: 文件大小
	:param Precision: 小数点
	:return: 格式化数字, 单位
	"""

	Units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]

	for Unit in Units:
		if abs(Byte) < 1024:
			return float(format(Byte, ".%df" % Precision)), Unit

		Byte /= 1024

	return float(format(Byte, ".%df" % Precision)), "Yi"

def getHead(URL: str):
	def TryGet():
		try:
			return requests.head(URL)
		except:
			return TryGet()

	return TryGet()

def downloadFile(URL: str,
				 Path=".\\",
				 ShowProgressBar=True,
				 MaxRetries=3,
				 ChunkSize=2048,
				 UseFileName=True,
				 OtherProgressBar=None,
				 DownloadFileName=None,
				 AutoRemoveProgressBar=True,
				 _CallBack=None,
				 IgnoreError=False) -> bool:
	"""
	下载文件

	下载文件并保存到文件

	:param URL: 文件下载连接
	:param Path: 下载位置
	:param ShowProgressBar: 是否显示进度条
	:param MaxRetries: 最大重试次数
	:param ChunkSize: 最大文件块大小
	:param UseFileName: 是否使用源文件的名字
	:param OtherProgressBar: rich.Progress对象，用于套用自定义进度条
	:param DownloadFileName: 文件名字 (前提是 UseFileName 为 True)
	:param AutoRemoveProgressBar: 下载完成自动移除进度条
	:param _CallBack: 内部操作, 在下载完成后调用函数
	:param IgnoreError: 禁用代码报错

	:return: 文件是否下载成功
	"""

	if not os.path.exists(Path):
		if not IgnoreError:
			return False
		else:
			raise errors.FolderNotFoundError(f"Cant find folder at \"{Path}\"")

	if os.path.isfile(Path):
		if not IgnoreError:
			return False
		else:
			raise errors.PathIsFileError(f"Path \"{Path}\" is a file")

	Path = Path.replace("/", "\\")
	if Path[-1] != "\\":
		Path += "\\"

	FileName = getFileName(URL)
	FileSuffix = ""

	if FileName is not None:
		FileSuffix = os.path.splitext(FileName)[-1]

	if DownloadFileName is not None:
		if os.path.exists(Path + DownloadFileName + FileSuffix):
			if not IgnoreError:
				return False
			else:
				raise errors.FileSystemError(f"A file with the same name was found in \"{Path}\"")

		FileName = DownloadFileName

	if FileName is None:
		if UseFileName and FileName == "":
			if not IgnoreError:
				return False
			else:
				raise errors.DownloadFailed("Cant get file name")

	if not UseFileName:
		FileName = newFileName(Path, FileSuffix)

	def TryDownload(MaxRetriesSize, ProgressBar, TaskID, FileSize):
		try:
			DoNotUseRem = False

			if FileSize > 1000:
				DoNotUseRem = True

			DownloadObject = requests.get(URL, stream=DoNotUseRem)

			with open(Path + FileName + FileSuffix, "wb") as File:
				if DoNotUseRem:
					for Chunk in DownloadObject.iter_content(chunk_size=ChunkSize):
						File.write(Chunk)

						if ProgressBar is not None:
							ProgressBar.advance(TaskID, len(Chunk))
				else:
					File.write(DownloadObject.content)

					if ProgressBar is not None:
						ProgressBar.advance(TaskID, len(DownloadObject.content))

			if ProgressBar is not None and AutoRemoveProgressBar:
				ProgressBar.remove_task(TaskID)

			if _CallBack is not None:
				_CallBack()

			return True
		except KeyboardInterrupt:
			if not IgnoreError:
				return False
			else:
				raise KeyboardInterrupt("Process has been forced to end")
		except:
			if MaxRetriesSize != 0:
				ProgressBar.reset(TaskID)

				return TryDownload(MaxRetriesSize - 1, ProgressBar, TaskID, FileSize)
			else:
				if ProgressBar is not None and AutoRemoveProgressBar:
					ProgressBar.remove_task(TaskID)

				if _CallBack is not None:
					_CallBack()

				return False

	open(Path + FileName + FileSuffix, "wb").close()

	Headers = getHead(URL)

	if Headers.status_code == requests.codes.ok:
		FileSize = int(Headers.headers["content-length"])
		FormatFileSize, Unit = byteFormat(FileSize)

		if ShowProgressBar:
			if OtherProgressBar is not None:
				MainTask = OtherProgressBar.add_task(f"Downloading {FileName + FileSuffix} ({str(FormatFileSize) + Unit})", total=FileSize)
				return TryDownload(MaxRetries, OtherProgressBar, MainTask, FileSize)
			else:
				with Progress() as ProgressBar:
					MainTask = ProgressBar.add_task(f"Downloading {FileName + FileSuffix} ({str(FormatFileSize) + Unit})", total=FileSize)

					return TryDownload(MaxRetries, ProgressBar, MainTask, FileSize)
		else:
			return TryDownload(MaxRetries, None, None, FileSize)
	else:
		os.remove(Path + FileName + FileSuffix)

def downloadFileList(URLList: list,
					 Path=".\\",
					 ShowProgressBar=True,
					 MaxRetries=3,
					 ChunkSize=2048,
					 Multithreading=False,
					 MaxThreadSize=5) -> [bool]:
	"""
	从列表中下载文件

	从列表中下载文件并保存到文件夹中

	:param URLList: 文件下载连接
	:param Path: 下载位置
	:param ShowProgressBar: 是否显示进度条
	:param MaxRetries: 最大重试次数
	:param ChunkSize: 最大文件块大小
	:param Multithreading: 是否使用多线程下载
	:param MaxThreadSize: 最大线程数量

	:return: 文件是否下载成功
	"""

	global ProgressNumber

	with Progress() as ProgressBar:
		DownloadList = ProgressBar.add_task("Downloading from list", total=len(URLList))
		ThreadSizeDisplay = ProgressBar.add_task("Thread count", total=MaxThreadSize)

		def Func():
			global ProgressNumber
			ProgressNumber -= 1

			ProgressBar.advance(ThreadSizeDisplay, -1)

			ProgressBar.update(ThreadSizeDisplay, description=f"Thread count ({ProgressNumber}/{len(threading.enumerate()) - 1})")

		def MainThread(URL):
			global ProgressNumber

			def DownloadMain(URL_):
				downloadFile(
						URL_,
						Path=Path,
						ShowProgressBar=ShowProgressBar,
						MaxRetries=MaxRetries,
						ChunkSize=ChunkSize,
						UseFileName=False,
						OtherProgressBar=ProgressBar,
						AutoRemoveProgressBar=True,
						_CallBack=Func,
						IgnoreError=True
					)

			Thread = threading.Thread(target=DownloadMain, args=(URL,))
			Thread.setDaemon(True)
			ProgressNumber += 1
			ProgressBar.advance(ThreadSizeDisplay)
			Thread.start()

		for i in URLList:
			if Multithreading:
				MainThread(i)

				while ProgressNumber >= MaxThreadSize:
					time.sleep(0.01)

				if ProgressNumber != len(threading.enumerate()) - 1:
					ProgressNumber = len(threading.enumerate()) - 1
			else:
				downloadFile(
					i,
					Path=Path,
					ShowProgressBar=ShowProgressBar,
					MaxRetries=MaxRetries,
					ChunkSize=ChunkSize,
					UseFileName=False,
					OtherProgressBar=ProgressBar,
					AutoRemoveProgressBar=True,
					IgnoreError=True
				)

			ProgressBar.advance(DownloadList, 1)

		while ProgressNumber != 0 and len(threading.enumerate()) != 1:
			time.sleep(0.01)