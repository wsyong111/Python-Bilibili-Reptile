"""
API接口:
	动态API:
		USER_ID: 用户ID
		NEXT_OFFSET: 偏移大小
"""

import json
import random
import time

from rich.traceback import install as TracebackRunner

from . import utils

TracebackRunner()

API_PATH = "./apiUrls.json"

API_LIST = utils.readJsonFile(API_PATH)


def getLiveContent(userID, nextOffset, progressBar):
	APIUrl = API_LIST["GetLiveContentAPI"].format(USER_ID=userID, NEXT_OFFSET=nextOffset)

	imageUrlList = []

	APIReturn, sendSuccess = utils.httpGet(APIUrl)

	if sendSuccess:
		jsonData = json.loads(APIReturn)["data"]

		nextOffset_ = jsonData["next_offset"]
		hasMore = jsonData["has_more"]

		if "cards" in jsonData:
			for cardData in jsonData["cards"]:
				cardData = cardData["card"]

				cardJsonData = json.loads(cardData)

				if cardData[2] == "i" or cardData[2] == "c":
					for item in cardJsonData["item"]["pictures"]:
						imageUrlList.append(item["img_src"])
				elif cardData[2] == "a":
					continue

		return imageUrlList, nextOffset_, hasMore
	else:
		progressBar.log("[red]\\[Error] 你已被API屏蔽，请稍后重试")

		exit(-1)


def onLoad(userIDList, progressBar):
	returnImageList = []
	sendRequests = 0

	mainProgressBar = progressBar.add_task(description="正在爬取UP主动态", total=len(userIDList))

	for userID in userIDList:
		progressBar.log(f"[green]\\[Log] 正在爬取UP主的动态: {userID}")

		hasMore = 1
		nextOffset = 0

		while hasMore == 1:
			imageUrlList, nextOffset_, hasMore_ = getLiveContent(userID, nextOffset, progressBar)

			nextOffset = nextOffset_
			hasMore = hasMore_

			progressBar.log(f"[green]\\[Log] 动态ID: {nextOffset}")

			returnImageList += imageUrlList

			sendRequests += 1

			time.sleep(random.randint(1, 10) / 10)

		progressBar.advance(mainProgressBar)

	progressBar.remove_task(mainProgressBar)

	return returnImageList, sendRequests
