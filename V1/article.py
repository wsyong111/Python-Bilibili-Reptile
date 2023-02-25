import json
import random
import time

import requests
from fake_useragent import UserAgent
from rich.console import Console
from bs4 import BeautifulSoup as BS

Console = Console()

RandomUserAgent = UserAgent()

def RandomHeaders():
	return {
		"user-agent": RandomUserAgent.random
	}

def GetArticleContent(ID):
	API = f"https://api.bilibili.com/x/article/view?id={ID}"

	ImageUrlList = []

	Object = requests.get(API, headers=RandomHeaders(), timeout=10)

	if Object.status_code == requests.codes.ok:
		JsonData = json.loads(Object.content)

		if "data" in JsonData:
			if "content" in JsonData["data"]:
				HtmlText = JsonData["data"]["content"]

				Html = BS(HtmlText, "html.parser")

				for ImageObject in Html.select("img"):
					ImageUrlList += ["https:" + ImageObject.get("src")]
	else:
		Console.log("[red]错误: 你已被API屏蔽，请稍后重试")
		exit(-1)

	return ImageUrlList

def GetAllArticle(UID, Page, MaxPage=30):
	API = f"https://api.bilibili.com/x/space/article?mid={UID}&pn={Page}&ps={MaxPage}&sort=publish_time&jsonp=jsonp"

	ImageUrls = []
	SendRequest = 0

	Object = requests.get(API, headers=RandomHeaders(), timeout=10)

	if Object.status_code == requests.codes.ok:
		JsonData = json.loads(Object.content)

		Data = JsonData["data"]

		if "articles" in Data:
			for Article in Data["articles"]:
				Console.log(f"ArticlesID: {Article['id']}")
				ImageUrls += GetArticleContent(Article["id"])

				SendRequest += 1

				time.sleep(random.randint(5, 10) / 10)
		else:
			return None, 0
	else:
		Console.log("[red]错误: 你已被API屏蔽，请稍后重试")
		exit(-1)

	return ImageUrls, SendRequest

def Load(UserIDList):
	ImageUrlList = []

	SendRequest = 0

	for UID in UserIDList:
		Console.log(f"正在爬取: {UID}")

		Index = 0

		while True:
			Index += 1

			Output, SendRequest_ = GetAllArticle(UID, Index)

			SendRequest += SendRequest_

			if Output is None:
				break
			else:
				ImageUrlList += Output

	return ImageUrlList, len(ImageUrlList), SendRequest