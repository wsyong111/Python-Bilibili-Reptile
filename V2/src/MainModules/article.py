"""
API接口:
	文章API:
		USER_ID: 用户ID
		PAGE: 页数
		MAX_PAGE: 最大页数

	文章内容API:
		ID: 文章ID
"""

import json
import random
import time

from bs4 import BeautifulSoup as BS4
from rich.traceback import install as TracebackRunner

from . import utils

TracebackRunner()

API_PATH = "./apiUrls.json"
API_LIST = utils.readJsonFile(API_PATH)
MAX_PAGE = 30


def getUserArticleContent(articleID, progressBar):
	APIUrl = API_LIST["GetArticleContentAPI"].format(ID=articleID)

	imageUrlList = []

	APIReturn, sendSuccess = utils.httpGet(APIUrl)

	if sendSuccess:
		jsonData = json.loads(APIReturn)["data"]

		if "content" in jsonData:
			htmlObject = BS4(jsonData["content"], "html.parser")

			for imageObject in htmlObject.select("img"):
				imageUrlList.append("https:" + imageObject.get("src"))
	else:
		progressBar.log("[red]\\[Error] 你已被API屏蔽，请稍后重试")
		exit(-1)

	return imageUrlList


def getUserAllArticle(userID, page, progressBar):
	APIUrl = API_LIST["ArticleAPI"].format(USER_ID=userID, PAGE=page, MAX_PAGE=MAX_PAGE)

	imageUrls = []
	sendRequest = 0

	APIReturn, sendSuccess = utils.httpGet(APIUrl)

	if sendSuccess:
		jsonData = json.loads(APIReturn)["data"]

		if "articles" in jsonData:
			for article in jsonData["articles"]:
				articleID = article["id"]

				progressBar.log(f"[green]\\[Log] 文章ID: {articleID}")

				imageUrls_ = getUserArticleContent(articleID, progressBar)

				imageUrls += imageUrls_

				sendRequest += 1

				time.sleep(random.randint(5, 10) / 10)
		else:
			return None, 0
	else:
		progressBar.log("[red]\\[Error] 你已被API屏蔽，请稍后重试")

		exit(-1)

	return imageUrls, sendRequest


def onLoad(userIDList, progressBar):  # 入口
	returnImageList = []
	sendRequests = 0

	mainProgressBar = progressBar.add_task(description="正在爬取UP主文章", total=len(userIDList))

	for userID in userIDList:
		progressBar.log(f"[green]\\[Log] 正在爬取UP主的文章: {userID}")

		index = 0
		while True:
			index += 1

			imageUrls, sendRequests_ = getUserAllArticle(userID, index, progressBar)

			sendRequests += sendRequests_

			if imageUrls is None:
				break
			else:
				returnImageList += imageUrls

		progressBar.advance(mainProgressBar)

	progressBar.remove_task(mainProgressBar)

	return returnImageList, sendRequests
