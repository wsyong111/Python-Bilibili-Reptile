import inspect
import os
import sys
import warnings
from typing import Union
import json


class PathObject(str):
	"""
	路径对象, 让路径编程更容易
	"""

	def __init__(self, path=os.getcwd()):
		self = os.path.abspath(path)

	def getDrive(self) -> str:
		"""
		获取路径的驱动器

		:return: 驱动器
		"""

		return os.path.splitdrive(self)[0]

	def getParent(self) -> str:
		"""
		返回路径的父文件夹名字

		:return: 父文件夹名字
		"""

		return os.path.dirname(self)

	def isFile(self) -> bool:
		"""
		测试路径是否为文件

		:return: 路径是否为文件
		"""

		return os.path.isfile(self)

	def isFolder(self) -> bool:
		"""
		测试路径是否为文件夹

		:return: 路径是否为文件夹
		"""

		return os.path.isdir(self)

	def findItem(self, name: str):
		"""
		在路径内查找给定名字的文件或文件夹

		:param name: 文件或文件夹的名字
		:return: 返回文件或文件夹的路径（如果找到的, 否则返回 None）
		"""

		if os.path.exists(self):
			for root, dirs, files in os.walk(self):
				for file in files:
					if file == name:
						return os.path.join(root, file)
				for folder in dirs:
					if folder == name:
						return os.path.join(root, folder)
			return None
		else:
			return None

	def list(self) -> Union[list, None]:
		if os.path.exists(self):
			return os.listdir(self)
		else:
			return None

	def valid(self) -> bool:
		return os.path.exists(self)

	def __sub__(self, n):
		return PathObject(os.path.abspath(os.path.join(self, *([".."] * n))))

	def __add__(self, other: str):
		stack = inspect.stack()
		callingScript = stack[1].filename

		if isPythonModule(callingScript):
			return str.__add__(self, other)

		return PathObject(os.path.realpath(os.path.abspath(os.path.join(self, other))))

	def __iadd__(self, other: str):
		return self.__add__(other)

	def __isub__(self, other: int):
		return self.__sub__(other)

	def __str__(self):
		return self


class Translate(object):
	"""
	翻译文件管理器
	"""

	_lang: str = "en"
	encoding: str = "utf-8"

	def __init__(self, translateFolder: Union[PathObject, str], showWarn: bool = True):
		if not os.path.isdir(translateFolder):
			raise IsADirectoryError("Is folder")

		stack = inspect.stack()
		self.callingScriptName = os.path.split(stack[1].filename)[-1].split(".", 1)[0]

		self.translateFolder = PathObject(translateFolder)

	def _getTranslateFolders(self) -> list:
		folderList = []
		for folder in os.listdir(self.translateFolder):
			if not os.path.isdir(os.path.join(self.translateFolder, folder)):
				continue

			if not len(folder.split("-")) >= 2:
				continue

			folderList.append(folder)

		return folderList

	def _loadFile(self, lang) -> dict:
		"""
		读取翻译文件

		:param lang: 翻译
		"""

		selectedFolder = ""

		if len(lang) == 2:
			for folder in self._getTranslateFolders():
				if folder.split("-")[0] == lang:
					selectedFolder = folder
					break
		else:
			if os.path.exists(os.path.join(self.translateFolder, lang)):
				selectedFolder = lang

		if selectedFolder == "":
			raise FileNotFoundError("Cant find translate folder")

		fileName = ""
		for file in os.listdir(selectedFolder):
			filePath = os.path.join(self.translateFolder, selectedFolder, file)

			if os.path.isfile(filePath):
				if file.split(".")[-1] != "json":
					continue

				spiltName = file.split(".")

				if spiltName[1] in ["exe", "py", "pyw"]:
					if spiltName[0] == self.callingScriptName:
						fileName = filePath
						break

		else:
			raise FileNotFoundError("Cant find translate file")

		try:
			with open(fileName, "r", encoding=self.encoding) as file:
				content = file.read()
		except Exception:
			raise IOError("Cant read translate file")

		try:
			return json.loads(content)
		except json.JSONDecodeError:
			raise IOError("Cant load translate file")

	def loadFile(self):
		self.translate = self._loadFile(self._lang)

	def getTranslate(self, tag: str) -> str:
		"""
		使用Tag获取翻译文字

		如果未找到翻译文本则使用英文原文

		:param tag: 翻译名字
		:return: 翻译文本
		"""

		translate = {}

		if self.translate is None:
			return ""

		if tag in self.translate:
			translate = self.translate
		else:
			try:
				translate = self._loadFile("en")

				warnings.warn(f"Translate key {tag} not in {self._lang}")
			except Exception:
				return ""

		if tag not in translate:
			return ""

		return translate[tag]

	def __getitem__(self, item: str):
		return self.getTranslate(item)

	def onLangChange(self, value):
		pass

	@property
	def lang(self):
		"""
		翻译语言
		"""

		return self._lang

	@lang.setter
	def lang(self, value: str):
		"""
		翻译语言
		"""

		self._lang = value

		self.onLangChange(value)


class JsonReader(object):
	"""
	Json文件读取器
	"""

	def __init__(self, jsonFile: Union[PathObject, str], encoding="utf-8"):
		if not os.path.exists(jsonFile):
			raise FileNotFoundError("Cant find json file")

		self.jsonFile = jsonFile

		self.reload()

	def reload(self) -> None:
		"""
		重新读取Json文件
		"""

		try:
			with open(self.jsonFile, "r") as file:
				self.content = json.loads(file.read())

		except IOError:
			raise IOError("Cant load json file")

		except json.JSONDecodeError:
			raise IOError("Cant decode json data")

	def getContent(self) -> dict:
		"""
		获取Json文件的内容

		:return: Json文件的内容
		"""

		return self.content

	def write(self, item: dict) -> None:
		"""
		将给定表格写入Json文件

		:param item: 表格
		"""

		try:
			with open(self.jsonFile, "w") as file:
				file.write(json.dumps(item))
		except PermissionError:
			raise PermissionError("Cant write json string to json file")
		except IOError:
			raise IOError("Cant write json string to json file")

		self.content = item

	def setValue(self, path: str, value: any) -> None:
		"""
		更改Json文件的内容

		格式为 path.to.key

		Json文件内容:
			{
				"Wong": {
					"age": 17,\n
					"name": "wong sheng yong"
				}
			}

		>>> jsonFile = JsonReader("./test.json")
		>>> jsonFile.setValue("Wong.age", 18)

		:param path: 数据路径
		:param value: 将path设定为value
		"""

		spiltPath = path.split(".")

		lastValue = self.content
		for pathName in spiltPath[0:-1]:
			if type(lastValue) != dict:
				raise TypeError("Value is not a dict")

			if pathName in lastValue:
				lastValue = lastValue[pathName]
			else:
				raise NameError(f"Cant find value at {pathName}")

		else:
			lastValue[spiltPath[-1]] = value

		self.write(self.content)

	def getValue(self, path: str) -> any:
		"""
		更改Json文件的内容

		格式为 path.to.key

		Json文件内容:
			{
				"Wong": {
					"age": 17,\n
					"name": "wong sheng yong"
				}
			}

		>>> jsonFile = JsonReader("./test.json")
		>>> print(jsonFile.getValue("Wong.age"))

		:param path: 数据路径
		:return:数据
		"""

		lastValue = self.content
		for pathName in path.split("."):
			if type(lastValue) != dict:
				raise TypeError("Value is not a dict")

			if pathName in lastValue:
				lastValue = lastValue[pathName]
			else:
				raise NameError(f"Cant find value at {pathName}")

		return lastValue


def isPythonModule(scriptPath: Union[PathObject, str]) -> bool:
	"""
	测试给定的脚本路径是否为python模块

	:param scriptPath: 脚本路径
	:return: 是否是python模块
	"""

	if scriptPath is not PathObject:
		scriptPath = os.path.abspath(scriptPath)

	if os.path.splitdrive(scriptPath)[0] == os.path.splitdrive(sys.prefix)[0]:
		for path in [os.path.join(sys.prefix, "lib"), os.path.join(sys.prefix, "lib", "site-packages")]:
			if os.path.commonpath([scriptPath, path]) == path:
				return True
	return False
