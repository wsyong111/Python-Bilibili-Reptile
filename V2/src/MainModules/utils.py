import json
import os

import chardet
import requests
from fake_useragent import UserAgent

randomUserAgent = UserAgent()


ALLOW_LOAD_JSON_TYPE = [
	".json",
	".mui"
]


def readJsonFile(filePath):
	if os.path.exists(filePath):
		if os.path.isfile(filePath) and os.path.splitext(filePath)[-1] in ALLOW_LOAD_JSON_TYPE:
			encode = "utf-8"

			with open(filePath, "rb") as f:
				encode = chardet.detect(f.read())["encoding"]

			with open(filePath, "r", encoding=encode) as file:
				return json.loads(file.read())
		else:
			raise IOError(f"\"{filePath}\" is not a JSON file")
	else:
		raise FileNotFoundError("File not found")


def saveJsonFile(filePath, table):
	with open(filePath, "w") as file:
		file.write(json.dumps(table))


def httpGet(url, maxTry=5, statusCode=requests.codes.ok):
	httpObject = None

	trySize = 0
	while True:
		if trySize >= maxTry:
			return None, False

		try:
			httpObject = requests.get(
				url,
				timeout=10,
				headers={
					"user-agent": randomUserAgent.random
				}
			)

		except requests.exceptions.ConnectionError:
			pass

		if httpObject is not None:
			if httpObject.status_code == statusCode:
				return httpObject.content, True

		trySize += 1
