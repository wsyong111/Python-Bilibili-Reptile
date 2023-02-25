import os
import threading
import time

import requests
from rich.console import Console
from rich.progress import Progress

console = Console()

MAX_THREAD_SIZE = 16
FILE_SIZE_UNITES = ["B ", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]

threadList = []


def formatFileSize(fileSize, precision=2):
	for unite in FILE_SIZE_UNITES:
		if abs(fileSize) < 1024:
			return float(format(fileSize, ".%df" % precision)), unite

		fileSize /= 1024

	return float(format(fileSize, ".%df" % precision)), "Yi"


def sendGetHeadRequest(url, maxTrySize=3, output=console.log):
	httpObject = None

	while maxTrySize > 0:
		try:
			httpObject = requests.head(url)
		except Exception:
			maxTrySize -= 1

		if httpObject is not None:
			if httpObject.status_code == requests.codes.ok:
				return httpObject.headers
			else:
				maxTrySize -= 1

	return None


def getFileName(url, output=console.log):
	splitUrl = url.lower().split("/")

	return splitUrl[-1].split("?")[0]


def clearStoppedThread():
	for thread in threadList:
		if not thread.is_alive():
			del threadList[threadList.index(thread)]


def downloadThread(url, path, progressBar, maxTrySize=10):
	fileName = getFileName(url)

	fileHead = sendGetHeadRequest(url, output=progressBar.log)

	if fileHead is None:
		progressBar.log(f"[red]\\[Error] ERR: {url}")
		return

	fileSize = int(fileHead["content-length"])
	formattedFileSize, fileSizeUnite = formatFileSize(fileSize)

	downloadProgressBar = progressBar.add_task(
		description=f"{fileName} ({formattedFileSize}{fileSizeUnite})",
		total=fileSize
	)

	fileDownloadPath = path + fileName

	progressBar.log(f"[green]\\[Log] GET: {url}")

	while maxTrySize > 0:
		try:
			if os.path.exists(fileDownloadPath):
				fileNormalSize = os.path.getsize(fileDownloadPath)
			else:
				fileNormalSize = 0

			headers = {
				"Range": "bytes=%d-" % fileNormalSize
			}

			with requests.get(url, stream=True, headers=headers) as fileHttpObject:
				if fileHttpObject.status_code == 206:
					with open(fileDownloadPath, "ab") as file:
						for chunk in fileHttpObject.iter_content(chunk_size=1024):
							if chunk:
								file.write(chunk)
								file.flush()

								progressBar.advance(downloadProgressBar, advance=len(chunk))

								fileNormalSize += len(chunk)

				progressBar.remove_task(downloadProgressBar)
				break

		except Exception:
			maxTrySize -= 1


def download(urlList, progressBar, path="./"):
	global threadList

	mainProgressBar = progressBar.add_task(description="正在从下载队列下载文件...", total=len(urlList))
	taskSizeBar = progressBar.add_task(description=f"线程占用 ({len(threadList)}/{MAX_THREAD_SIZE})", total=MAX_THREAD_SIZE)

	lastThreadSize = 0

	for url in urlList:
		while len(threadList) >= MAX_THREAD_SIZE:
			clearStoppedThread()

			if lastThreadSize != len(threadList):
				lastThreadSize = len(threadList)

				progressBar.reset(taskSizeBar)
				progressBar.update(taskSizeBar, description=f"线程占用 ({len(threadList)}/{MAX_THREAD_SIZE})")
				progressBar.advance(taskSizeBar, advance=len(threadList))

			time.sleep(0.1)

		progressBar.advance(mainProgressBar)

		clearStoppedThread()

		downloadThreadMain = threading.Thread(target=downloadThread, args=(url, path, progressBar))
		downloadThreadMain.setDaemon(True)
		downloadThreadMain.start()

		threadList.append(downloadThreadMain)

	while len(threadList) > 0:
		clearStoppedThread()

		time.sleep(0.1)

	progressBar.remove_task(mainProgressBar)
	progressBar.remove_task(taskSizeBar)


if __name__ == "__main__":
	DOWN_LIST = [
		"https://i0.hdslb.com/bfs/article/cd444cce2726e68cb62d2c997eab40d58485e9e2.jpg",
		"https://i0.hdslb.com/bfs/article/95c850539d21668b2be510d7bc39d6ac35e2ea95.jpg",
		"https://i0.hdslb.com/bfs/article/95c850539d21668b2be510d7bc39d6ac35e2ea95.jpg",
		"https://i0.hdslb.com/bfs/article/900974c38b621df2aa02bf859e2202d623420acb.jpg",
		"https://i0.hdslb.com/bfs/article/6fb15d727b58e29d67f32e30c1d886fa8348b830.jpg",
		"https://i0.hdslb.com/bfs/article/44acdd5c4a524d5fe3daf3e8fa0fe10305791974.jpg",
		"https://i0.hdslb.com/bfs/article/44acdd5c4a524d5fe3daf3e8fa0fe10305791974.jpg",
		"https://i0.hdslb.com/bfs/album/b408b251f28addac1893c5646de962d2e10c8d0b.jpg?from=bili",
		"https://i0.hdslb.com/bfs/article/6fb15d727b58e29d67f32e30c1d886fa8348b830.jpg",
		"https://i0.hdslb.com/bfs/article/71e3d48f2ccc1fa6eaf5ff67e744fc46512380bd.jpg",
		"https://i0.hdslb.com/bfs/article/71e3d48f2ccc1fa6eaf5ff67e744fc46512380bd.jpg",
		"https://i0.hdslb.com/bfs/article/aa732f0c605421ef8b023b6cf126cef1a9b0198b.jpg",
		"https://i0.hdslb.com/bfs/article/1bf078cad92a0e35bc617455d148b6051b39e48a.jpg",
		"https://i0.hdslb.com/bfs/article/04a96f26001cf14c80b5400c13de8ea763c605f5.jpg",
		"https://i0.hdslb.com/bfs/article/aa732f0c605421ef8b023b6cf126cef1a9b0198b.jpg",
		"https://i0.hdslb.com/bfs/article/3a9a8286099bd6d2f3d795ac8adeffd4eabce973.jpg",
		"https://i0.hdslb.com/bfs/article/fad05b062eaa4b8961c12f0b9b28caae897d2188.jpg",
		"https://i0.hdslb.com/bfs/article/baa709e823e8bdbdbebd0f57e7517423df7254ed.jpg",
		"https://i0.hdslb.com/bfs/article/fad05b062eaa4b8961c12f0b9b28caae897d2188.jpg",
		"https://i0.hdslb.com/bfs/article/baa709e823e8bdbdbebd0f57e7517423df7254ed.jpg",
		"https://i0.hdslb.com/bfs/article/a39feb87cbe427e887e9b5b0d101efa673916184.jpg",
		"https://i0.hdslb.com/bfs/article/34e9719ed89cd7b3e64b8671ca196cf9d2861aa0.jpg",
		"https://i0.hdslb.com/bfs/article/a39feb87cbe427e887e9b5b0d101efa673916184.jpg",
		"https://i0.hdslb.com/bfs/article/34e9719ed89cd7b3e64b8671ca196cf9d2861aa0.jpg",
		"https://i0.hdslb.com/bfs/article/cd444cce2726e68cb62d2c997eab40d58485e9e2.jpg",
	]

	with Progress() as progressBar:
		download(DOWN_LIST, progressBar, path="./../Download/")
