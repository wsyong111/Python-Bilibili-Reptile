import json
import random
import time
from fake_useragent import UserAgent
from rich.console import Console
import requests

RandomUserAgent = UserAgent()

Console = Console()

def RandomHeaders():
	return {
		"user-agent": RandomUserAgent.random
	}

def GetBilibiliContent(NextOffset, UserId):
	API = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid={UserId}&host_uid={UserId}&offset_dynamic_id={NextOffset}&need_top=1&platform=web"

	UrlList = []

	Object = requests.get(API, headers=RandomHeaders(), timeout=10)

	if Object.status_code == requests.codes.ok:
		JsonData = json.loads(Object.content)

		NextOffset_ = JsonData["data"]["next_offset"]
		HasMore = JsonData["data"]["has_more"]

		if "cards" in JsonData["data"]:
			for DictData in JsonData["data"]["cards"]:
				SubJsonData = json.loads(DictData["card"])

				if DictData["card"][2] == "i" or DictData["card"][2] == "c":
					for Item in SubJsonData["item"]["pictures"]:
						UrlList.append(Item["img_src"])
				elif DictData["card"][2] == "a":
					continue

		return UrlList, NextOffset_, HasMore
	else:
		Console.log("[red]错误: 你已被API屏蔽，请稍后重试")
		exit(-1)

def Load(UserIDList):
	ImageURLList = []
	GetImage = 0
	GetApi = 0

	for UID in UserIDList:
		NextOffset = 0
		HasMore = 1
		Console.log(f"正在爬取 {UID}")

		while HasMore == 1:
			ImageList, NextOffset_, HasMore_ = GetBilibiliContent(NextOffset, UID)

			NextOffset = NextOffset_
			HasMore = HasMore_

			Console.log(f"NextOffset: {NextOffset}")

			ImageURLList += ImageList

			GetImage += len(ImageList)
			GetApi += 1

			time.sleep(random.randint(1, 10) / 10)

		time.sleep(random.randint(10, 30) / 10)

	return ImageURLList, GetImage, GetApi