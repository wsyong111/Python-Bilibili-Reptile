"""
API接口:
	UP主状态API:
		USER_ID: 用户ID
"""

import curses
import json
import math
import os
import re
import string
import subprocess
import sys
import textwrap
import threading
import time
from sys import exit

import core
from MainModules import utils

DONT_USE_GUI_COMPONENTS = False

try:
	win32api = __import__("win32api")
	tkinter = __import__("tkinter")
	filedialog = __import__("tkinter.filedialog")

except ImportError:
	print("Err")

	DONT_USE_GUI_COMPONENTS = True

scr = curses.initscr()
scr.keypad(True)
curses.cbreak(True)
curses.noecho()
curses.start_color()

SCRIPT_NAME = os.path.basename(os.path.basename(sys.argv[0]))
SCRIPT_PATH = os.path.dirname(sys.argv[0])

CONFIG_FILE_PATH = "./settings.json"
API_FILE_PATH = "./apiUrls.json"
TRANSLATES_FILE_PATH = f"./{SCRIPT_NAME}.mui"

VERSION = "Reptile GUI V2.0"
API_LIST = utils.readJsonFile(API_FILE_PATH)
SELECTED_COLOR = 3
BACKGROUND_COLOR = 4
TEXT_COLOR = 5
TEMP_COLOR = 6
EXPLANATION_SIZE = 45
MAX_DISPLAY_VALUE_SIZE = 20

windowSizeX = 0
windowSizeY = 0

windowSizeChangeEvent = []

config = {}
translates = utils.readJsonFile(TRANSLATES_FILE_PATH)

"""
 ┌──────────┬────────────┐\n
 │ Color ID │ Color Name │\n
 ├──────────┼────────────┤\n
 │ 0        │ BLACK      │\n
 │ 1        │ BLUE       │\n
 │ 2        │ GREEN      │\n
 │ 3        │ CYAN       │\n
 │ 4        │ RED        │\n
 │ 5        │ MAGENTA    │\n
 │ 6        │ YELLOW     │\n
 │ 7        │ WHITE      │\n
 └──────────┴────────────┘
"""


# --------------------------------------------------------底层代码--------------------------------------------------------
def runCommand(command):
	process = subprocess.run([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

	return process.returncode


def openFolder(path):
	if not DONT_USE_GUI_COMPONENTS:
		win32api.ShellExecute(0, "open", os.path.abspath(path), "", "", 1)


def selectFolder():
	if not DONT_USE_GUI_COMPONENTS:
		win = tkinter.Tk()
		win.withdraw()

		return filedialog.askdirectory()

	return ""


def endwin():
	scr.keypad(False)
	curses.cbreak(False)
	curses.echo()

	curses.endwin()


def toKey(keyCode: int):
	if type(keyCode) == int:
		key = chr(keyCode)

		if key in list(string.ascii_letters + string.digits + " 	" + string.punctuation):
			return key

		return ""

	return None


def loadConfig():
	global config

	config = utils.readJsonFile(CONFIG_FILE_PATH)


def saveConfig():
	utils.saveJsonFile(CONFIG_FILE_PATH, config)


def clamp(x, min_=0, max_=math.inf):
	return max(min_, min(x, max_))


def len_(__obj, add=2, noEnter=False):
	if type(__obj) != str:
		return len(__obj)
	else:
		size = 0

		if noEnter:
			__obj = __obj.strip()

		for text in list(__obj):
			if re.fullmatch(r'[\u4e00-\u9fff]+', text):
				size += add
			else:
				size += 1

		return size


def subText(text, size=5):
	textList = []

	for t in text.split("\n"):
		textList.append("\n".join(textwrap.wrap(t, width=size)))

	return "\n".join(textList).split("\n")


def subTextSize(text, size=5):
	if len_(text) > size:
		return text[:size - 3] + "..."
	else:
		return text


# --------------------------------------------------------底层代码--------------------------------------------------------

# --------------------------------------------------------函数代码--------------------------------------------------------
def checkMid(midList):
	errorMid = []

	for mid in midList:
		APIUrl = API_LIST["GetUpStatus"].format(USER_ID=mid)

		httpObject, success = utils.httpGet(APIUrl)

		if success:
			jsonData = json.loads(httpObject)

			if jsonData["code"] != 0:
				errorMid.append(mid)

	return errorMid


def addstr(y, x, text, color=curses.color_pair(0), outputScr=scr):
	index = 0

	for v in list(text):
		outputScr.addstr(y, index + x, v, color)

		# if config["GUISettings"]["EmulatesOldConsole"]:
		# 	outputScr.refresh()
		#
		# 	curses.napms(10)

		if config["GUISettings"]["ShowSupportMode"]:
			index += len_(v)
		else:
			index += 1

	if config["GUISettings"]["EmulatesOldConsole"]:
		outputScr.refresh()

		curses.napms(10)


def addXLine(y, x=0, outputScr=scr):
	sizeY, sizeX = outputScr.getmaxyx()

	outputScr.addstr(y, x, "├" + ("─" * (sizeX - x - 2)) + "┤")


def addYLine(x, y=0, outputScr=scr):
	sizeY, sizeX = outputScr.getmaxyx()

	addstr(y, x, "┬", outputScr=scr)

	for i in range(sizeY - y - 2):
		addstr(i + y + 1, x, "│", outputScr=scr)

	addstr(sizeY - 1, x, "┴", outputScr=scr)


def confirmBox(title="Not name", text="Not about", normal=True):
	scr.refresh()
	scrSizeY, scrSizeX = scr.getmaxyx()

	sizeX = clamp(len_(max([title, text], key=len), add=3), 20, 50)

	text = subText(text, sizeX - 3)

	sizeY = clamp(len(text) + 6, 8)

	positionX = int((scrSizeX - sizeX) / 2)
	positionY = int((scrSizeY - sizeY) / 2)

	subScr = curses.newwin(sizeY, sizeX, positionY, positionX)
	subScr.bkgd(curses.color_pair(TEXT_COLOR))
	subScr.box()
	subScr.keypad(True)

	addstr(1, int((sizeX - len_(title)) / 2), title, outputScr=subScr)
	addstr(2, 0, "├" + ("─" * (sizeX - 2)) + "┤", outputScr=subScr)

	index = 0
	for t in text:
		addstr(index + 3, 2, t, outputScr=subScr)

		index += 1

	addstr(sizeY - 3, 0, "├" + ("─" * (sizeX - 2)) + "┤", outputScr=subScr)

	selected = 0

	if not normal:
		selected = 1

	def flush():
		yesSelect = curses.color_pair(0)
		noSelect = curses.color_pair(0)

		pos = 2

		if selected == 0:
			yesSelect = curses.color_pair(SELECTED_COLOR)
		else:
			noSelect = curses.color_pair(SELECTED_COLOR)

			pos = sizeX - 4

		addstr(sizeY - 2, 2, "Yes", yesSelect, outputScr=subScr)
		addstr(sizeY - 2, sizeX - 4, "No", noSelect, outputScr=subScr)

		subScr.move(sizeY - 2, pos)

		subScr.refresh()

	flush()

	while True:
		keycode = subScr.getch()

		if keycode == curses.KEY_LEFT or keycode == ord("a"):
			if selected > 0:
				selected -= 1
		elif keycode == curses.KEY_RIGHT or keycode == ord("d"):
			if selected < 1:
				selected += 1
		elif keycode == 10:
			del subScr

			if selected == 0:
				return True
			else:
				return False

		flush()


def msgBox(title="Not name", text="Not about"):
	scr.refresh()
	scrSizeY, scrSizeX = scr.getmaxyx()

	sizeX = clamp(len_(max([title, text], key=len)), 20, 50)

	text = subText(text, sizeX - 3)

	sizeY = len(text) + 6

	positionX = int((scrSizeX - sizeX) / 2)
	positionY = int((scrSizeY - sizeY) / 2)

	subScr = curses.newwin(sizeY, sizeX, positionY, positionX)
	subScr.bkgd(curses.color_pair(TEXT_COLOR))
	subScr.box()
	subScr.keypad(True)

	addstr(1, int((sizeX - len_(title)) / 2), title, outputScr=subScr)

	addXLine(2, outputScr=subScr)

	for i, t in enumerate(text):
		addstr(i + 3, 2, t, outputScr=subScr)

	addXLine(sizeY - 3, outputScr=subScr)

	addstr(sizeY - 2, int((sizeX - 2) / 2), "ok", curses.color_pair(SELECTED_COLOR), outputScr=subScr)

	while True:
		keycode = subScr.getch()

		if keycode == 10:
			subScr.clear()
			subScr.refresh()

			del subScr

			break


def selectListFunc(title="Not name", selectList=None):
	if selectList is None:
		selectList = [("true", True), ("false", False)]

	scr.refresh()
	scrSizeY, scrSizeX = scr.getmaxyx()

	sizeX = 0
	sizeY = len(selectList) + 4

	for i in selectList:
		if len_(i[0]) + 5 > sizeX:
			sizeX = len_(i[0]) + 5

	if len_(title) > sizeX:
		sizeX = len_(title) + 5

	sizeX = clamp(sizeX, 20)

	positionX = int((scrSizeX - sizeX) / 2)
	positionY = int((scrSizeY - sizeY) / 2)

	subScr = curses.newwin(sizeY, sizeX, positionY, positionX)
	subScr.bkgd(curses.color_pair(TEXT_COLOR))
	subScr.box()
	subScr.keypad(True)

	addstr(1, int((sizeX - len_(title)) / 2), title, outputScr=subScr)

	addXLine(2, outputScr=subScr)

	selected = 0

	def flush():
		for i, v in enumerate(selectList):
			color = curses.color_pair(0)

			if i == selected:
				color = curses.color_pair(SELECTED_COLOR)

			addstr(i + 3, int((sizeX - len_(v[0])) / 2), v[0], color, outputScr=subScr)

	flush()

	while True:
		keycode = subScr.getch()

		if keycode == ord("w") or keycode == curses.KEY_UP:
			if selected > 0:
				selected -= 1

		elif keycode == ord("s") or keycode == curses.KEY_DOWN:
			if selected < len(selectList) - 1:
				selected += 1

		elif keycode == 10:
			del subScr

			return selectList[selected][1]

		elif keycode == ord("q"):
			subScr.clear()
			subScr.refresh()

			del subScr

			return None

		flush()


def clearZone(positionX1, positionY1, positionX2, positionY2, outputScr=scr):
	posY = positionY1

	while True:
		posX = positionX1

		while True:
			outputScr.addstr(posY, posX, " ")

			posX += 1

			if posX == positionX2:
				break

		if posY == positionY2:
			break

		posY += 1


def inputBox(title, defaultText=""):
	curses.curs_set(True)

	sizeX = clamp(len_(title) + 4, 25, windowSizeX - 10)
	sizeY = 5

	positionX = int((windowSizeX - sizeX) / 2)
	positionY = int((windowSizeY - sizeY) / 2)

	subScr = curses.newwin(sizeY, sizeX, positionY, positionX)
	subScr.bkgd(curses.color_pair(TEXT_COLOR))
	subScr.keypad(True)
	subScr.box()

	addstr(1, int((sizeX - len_(title)) / 2) + 1, title, outputScr=subScr)
	addXLine(2, outputScr=subScr)

	text = defaultText

	def flush():
		addstr(3, 2, " " * (sizeX - 3), outputScr=subScr)

		if len(text) + 2 >= sizeX:
			addstr(3, 2, text[len(text) - (sizeX - 4):], outputScr=subScr)
		else:
			addstr(3, 2, text, outputScr=subScr)

		if len(text) == 0:
			subScr.move(3, 2)

		subScr.refresh()

	flush()

	while True:
		keycode = subScr.getch()

		if keycode == 10 or keycode == curses.KEY_BREAK:
			subScr.clear()
			subScr.refresh()

			del subScr

			curses.curs_set(False)

			return text

		elif keycode == 8:
			text = text[:len(text) - 1]

		else:
			text += toKey(keycode)

		flush()


# --------------------------------------------------------函数代码--------------------------------------------------------

selectedTab = 0

selectedConfig = 0
maxConfigSize = 0
mainMenuSelected = 0
enterPress = False
upKeyPress = False
downKeyPress = False


def listFunction(value, lang, selectList, isChangeLang=False):
	changeLang = True

	if isChangeLang and lang == "en":
		changeLang = confirmBox(
			title="Change language?",
			text="Switching to a language other than English may cause garbled characters on the settings interface",
			normal=False
		)

	if changeLang:
		select = selectListFunc(title=translates["Change_Language"][lang], selectList=selectList)

		if select is not None:
			if select != lang:
				text = translates["0x0000"][lang]
				title = translates["Message"][lang]

				msgBox(title=title, text=text)

			return select
		else:
			return lang
	else:
		return lang


def listControl(value, lang):
	title = translates["List_Controller"][lang]

	sizeX = 0
	if len(value) == 0:
		sizeX = 41
	else:
		sizeX = clamp(len(max(value, key=len)), 41)

	sizeY = clamp(len(value) + 4, 16, int(windowSizeY / 2) + 4)

	positionX = int((windowSizeX - sizeX) / 2)
	positionY = int((windowSizeY - sizeY) / 2)

	addItemText = "{{" + (" " * (int((sizeX - 5) / 2))) + "+}}"

	value.append(addItemText)

	subScr = curses.newwin(sizeY, sizeX, positionY, positionX)
	subScr.bkgd(curses.color_pair(TEXT_COLOR))
	subScr.keypad(True)

	def guiFrame():
		subScr.box()

		addstr(1, int((sizeX - len_(title)) / 2), title, outputScr=subScr)
		addXLine(2, outputScr=subScr)

		addXLine(sizeY - 3, outputScr=subScr)

		addstr(sizeY - 2, 2, "Q quit  UP up  DOWN down  ENTER Select", outputScr=subScr)

	guiFrame()

	displayPosition = 0
	changedValue = []
	selected = 0

	def flush():
		clearZone(1, 3, sizeX - 1, sizeY - 4, outputScr=subScr)

		cValue = value[displayPosition:displayPosition + sizeY - 7]

		if len(value[0:displayPosition + sizeY - 7]) < len(value) - 1:
			outputText = f"{len(value) - (sizeY - 7) - 1 - displayPosition}+"

			addstr(sizeY - 4, int((sizeX - len(outputText)) / 2), outputText, outputScr=subScr)
		else:
			cValue = value[displayPosition:displayPosition + sizeY - 6]

		for i, v in enumerate(cValue):
			color = curses.color_pair(0)

			isAddMode = False

			text = v
			if text == addItemText:
				text = v[2:-2]
				isAddMode = True

			if i + displayPosition == selected:
				color = curses.color_pair(SELECTED_COLOR)

				if not isAddMode:
					addstr(i + 3, 1, ">", color, outputScr=subScr)

			addstr(i + 3, 2, text, color, outputScr=subScr)

		subScr.refresh()

	def editList():
		def delf():
			if value[selected] in changedValue:
				changedValue.remove(value[selected])

			del value[selected]

		def editf():
			lastValue = value[selected]

			title = translates["Edit_Value"][lang]

			newValue = "A"

			while not newValue.isnumeric():
				newValue = inputBox(title=title, defaultText=lastValue)

				if newValue == "":
					break

			if newValue != "":
				if lastValue in changedValue:
					changedValue[changedValue.index(lastValue)] = newValue

				value[selected] = newValue

		selects = [
			{
				"name": translates["Remove_Value"],

				"call": delf
			},

			{
				"name": translates["Edit_Value"],

				"call": editf
			}
		]

		sizeX1 = 0

		for value1 in selects:
			if len_(value1["name"][lang]) > sizeX1:
				sizeX1 = len_(value1["name"][lang])

		sizeX1 += 3

		sizeY1 = len(selects) + 2

		positionX1 = int((windowSizeX - sizeX1) / 2)
		positionY1 = int((windowSizeY - sizeY1) / 2)

		subScr1 = curses.newwin(sizeY1, sizeX1, positionY1, positionX1)
		subScr1.bkgd(curses.color_pair(TEXT_COLOR))
		subScr1.keypad(True)
		subScr1.box()

		selected1 = 0

		def flush():
			for index, value1 in enumerate(selects):
				color = curses.color_pair(0)

				addText = " "

				if index == selected1:
					color = curses.color_pair(SELECTED_COLOR)
					addText = ">"

				addstr(index + 1, 1, addText + value1["name"][lang], color, outputScr=subScr1)

			subScr1.refresh()

		flush()

		while True:
			keycode = subScr1.getch()

			if keycode == 10:
				selects[selected1]["call"]()

				subScr1.clear()
				subScr1.refresh()

				del subScr1

				break

			elif keycode == curses.KEY_UP or keycode == ord("w"):
				if selected1 > 0:
					selected1 -= 1

			elif keycode == curses.KEY_DOWN or keycode == ord("s"):
				if selected1 < len(selects) - 1:
					selected1 += 1

			elif keycode == ord("q"):
				subScr1.clear()
				subScr1.refresh()

				del subScr1

				break

			flush()

	def addItem():
		title = translates["Add_Value"][lang]

		var = "A"

		while not var.isnumeric():
			var = inputBox(title=title)

			if var == "":
				break

		if var != "":
			value.insert(len(value) - 1, var)
			changedValue.append(var)

	flush()

	while True:
		keycode = subScr.getch()

		if keycode == curses.KEY_UP or keycode == ord("w"):
			if selected > 0:
				selected -= 1

			if selected < displayPosition:
				displayPosition -= 1

		elif keycode == curses.KEY_DOWN or keycode == ord("s"):
			if selected < len(value) - 1:
				selected += 1

			if len(value[0:displayPosition + sizeY - 7]) < len(value) - 1:
				if selected > displayPosition + sizeY - 8:
					displayPosition += 1

		elif keycode == curses.KEY_PPAGE:
			selected = 0
			displayPosition = 0

		elif keycode == curses.KEY_NPAGE:
			selected = len(value) - 1
			displayPosition = clamp(len(value) - 9, 0)

		elif keycode == 10:
			if value[selected] == addItemText:
				addItem()
			else:
				editList()

			subScr.refresh()

		elif keycode == ord("q"):
			text = translates["0x0001"][lang]

			sizeX1 = len_(text) + 3
			sizeY1 = 3

			positionX1 = int((windowSizeX - sizeX1) / 2)
			positionY1 = int((windowSizeY - sizeY1) / 2)

			subScr1 = curses.newwin(sizeY1, sizeX1, positionY1, positionX1)
			subScr1.bkgd(curses.color_pair(TEXT_COLOR))
			subScr1.box()

			addstr(1, 2, text, outputScr=subScr1)

			subScr1.refresh()

			success = checkMid(changedValue)

			if len(success) != 0:
				title = translates["Error"][lang]
				text = translates["0x0002"][lang]

				subScr1.clear()
				subScr1.refresh()

				del subScr1

				msgBox(title=title, text=text.format(SIZE=str(len(success))))

				guiFrame()
			else:
				del subScr

				return value[0:-1]

		flush()


def mainTabMain(lang):
	global mainMenuSelected, upKeyPress, downKeyPress, enterPress

	displaySelects = [
		{
			"text": translates["Run_Reptile"],

			"call": lambda: {
				endwin(),
				core.main(),
				exit()
			}
		},

		{
			"text": translates["0x000A"],

			"call": lambda: openFolder(config['ReptileSettings']['OutputFolder'])
		},

		{
			"text": translates["Exit"],

			"call": lambda: {
				endwin(),
				exit()
			}
		}
	]

	sizeX = 0

	findList = [
		*displaySelects,
		VERSION
	]

	for value in findList:
		if sizeX < len_(value):
			sizeX = len_(value)

	sizeX += 5

	sizeY = len(displaySelects) + 3

	positionX = int(((windowSizeX - EXPLANATION_SIZE) / 2) - (sizeX / 2))
	positionY = int(((windowSizeY + 3) / 2) - sizeY)

	addstr(positionY, positionX, "┌" + ("─" * (sizeX - 2)) + "┐")

	for i in range(sizeY - 1):
		addstr(positionY + i + 1, positionX, "│" + (" " * (sizeX - 2)) + "│")

	addstr(positionY + 2, positionX, "├" + ("─" * (sizeX - 2)) + "┤")
	addstr(positionY + sizeY, positionX, "└" + ("─" * (sizeX - 2)) + "┘")

	addstr(positionY + 1, positionX + int((sizeX - len_(VERSION)) / 2) + 1, VERSION)

	def flush():
		for index, value in enumerate(displaySelects):
			color = curses.color_pair(0)

			if index == mainMenuSelected:
				color = curses.color_pair(SELECTED_COLOR)

				addstr(positionY + 3 + index, positionX + 1, ">", color)

			addstr(positionY + 3 + index, positionX + 2, value["text"][lang], color)

		scr.refresh()

	if upKeyPress:
		upKeyPress = False

		if mainMenuSelected > 0:
			mainMenuSelected -= 1

	elif downKeyPress:
		downKeyPress = False

		if mainMenuSelected < len(displaySelects) - 1:
			mainMenuSelected += 1

	elif enterPress:
		enterPress = False

		displaySelects[mainMenuSelected]["call"]()

	flush()


def pathFunc(value, lang):
	def edit():
		newValue = selectFolder()

		if newValue != "":
			path = os.path.relpath(newValue, SCRIPT_PATH)

			if ".." not in path:
				path = "./" + path + "/"
			else:
				path = os.path.abspath(path)

			return path
		else:
			return value

	def show():
		text = translates["Opening_Explorer"][lang]

		sizeX1 = len_(text) + 3
		sizeY1 = 3

		positionX1 = int((windowSizeX - sizeX1) / 2)
		positionY1 = int((windowSizeY - sizeY1) / 2)

		subScr1 = curses.newwin(sizeY1, sizeX1, positionY1, positionX1)
		subScr1.bkgd(curses.color_pair(TEXT_COLOR))
		subScr1.box()

		addstr(1, 2, text, outputScr=subScr1)

		subScr1.refresh()

		openFolder(value)

		subScr1.clear()
		subScr1.refresh()

		del subScr1

		return value

	fileType = ""

	if os.path.exists(value):
		if os.path.isfile(value):
			fileType = translates["File"][lang]
		else:
			fileType = translates["Folder"][lang]

	fileType = fileType.lower()

	selects = [
		{
			"name": translates["Edit_Path"],

			"call": edit
		},

		{
			"name": translates["Show_File_Location"],

			"call": show
		}
	]

	title = translates["Path_Editor"][lang]

	sizeX = len_(title)

	for v in selects:
		if len(v["name"][lang]) > sizeX:
			sizeX = len(v["name"][lang])

	sizeX += 3

	sizeY = len(selects) + 4

	positionX = int((windowSizeX - sizeX) / 2)
	positionY = int((windowSizeY - sizeY) / 2)

	subScr = curses.newwin(sizeY, sizeX, positionY, positionX)
	subScr.bkgd(curses.color_pair(TEXT_COLOR))
	subScr.keypad(True)
	subScr.box()

	addstr(1, int((sizeX - len_(title)) / 2), title, outputScr=subScr)
	addXLine(2, outputScr=subScr)

	selected = 0

	def flush():
		for index, v in enumerate(selects):
			addText = " "

			color = curses.color_pair(0)

			if index == selected:
				color = curses.color_pair(SELECTED_COLOR)

				addText = ">"

			addstr(index + 3, 2, addText + v["name"][lang].format(FILE_TYPE=fileType), color, outputScr=subScr)

		subScr.refresh()

	flush()

	while True:
		keycode = subScr.getch()

		if keycode == 10:
			value = selects[selected]["call"]()

			subScr.clear()
			subScr.refresh()

			del subScr

			break

		elif keycode == ord("q"):
			subScr.clear()
			subScr.refresh()

			del subScr

			break

		elif keycode == curses.KEY_DOWN or keycode == ord("s"):
			if selected < len(selects) - 1:
				selected += 1

		elif keycode == curses.KEY_UP or keycode == ord("w"):
			if selected > 0:
				selected -= 1

		flush()

	return value


def colorFunc(value, lang):
	cursesColors = []

	colorNameList = translates["1x0000"]

	for v in dir(curses):
		if v.startswith("COLOR_") and v != "COLOR_PAIRS":
			cursesColors.append([
				getattr(curses, v),
				colorNameList[v[6:]][lang]
			])

	title = translates["Edit_Color"][lang]

	sizeX = len_(title)

	for v in cursesColors:
		if len_(v[1]) > sizeX:
			sizeX = len_(v[1])

	sizeX += 7

	sizeY = len(cursesColors) + 4

	positionX = int((windowSizeX - sizeX) / 2)
	positionY = int((windowSizeY - sizeY) / 2)

	subScr = curses.newwin(sizeY, sizeX, positionY, positionX)
	subScr.bkgd(curses.color_pair(TEXT_COLOR))
	subScr.keypad(True)
	subScr.box()

	addstr(1, int((sizeX - len_(title)) / 2) + 1, title, outputScr=subScr)

	addXLine(2, outputScr=subScr)

	selected = 0

	def flush():
		for index, v in enumerate(cursesColors):
			color = curses.color_pair(0)

			addStr = " "

			if selected == index:
				color = curses.color_pair(SELECTED_COLOR)
				addStr = ">"

			addstr(index + 3, 1, addStr + v[1], color, outputScr=subScr)

	flush()

	while True:
		keycode = subScr.getch()

		if keycode == ord("q"):
			break

		elif keycode == 10:
			value = cursesColors[selected][0]

			break

		elif keycode == curses.KEY_UP or keycode == ord("w"):
			if selected > 0:
				selected -= 1

		elif keycode == curses.KEY_DOWN or keycode == ord("s"):
			if selected < len(cursesColors) - 1:
				selected += 1

		flush()

	subScr.clear()
	subScr.refresh()

	del subScr

	return value


changeValueFunctions = {
	"bool": lambda value, lang: not value,
	"select": listFunction,
	"list": listControl,
	"path": pathFunc,
	"color": colorFunc
}

settingMappingTable = {
	"StartUp": {
		"__cfg__": {
			"name": translates["Main_Tab"],

			"isSetting": False
		},

		"call": "mainTabMain"
	},

	"ReptileSettings": {
		"__cfg__": {
			"name": translates["Reptile_Settings"],
			"isSetting": True
		},

		"ShowReport": {
			"type": "bool",
			"name": translates["Show_Report"],
			"explanation": translates["0x0009"]
		},

		"UserList": {
			"type": "list",
			"name": translates["User_List"],
			"explanation": translates["0x0008"]
		},

		"OutputFolder": {
			"type": "path",
			"name": translates["Image_Output_Path"],
			"explanation": translates["0x0007"]
		}
	},

	"GUISettings": {
		"__cfg__": {
			"name": translates["Gui_Settings"],
			"isSetting": True
		},

		"EmulatesOldConsole": {
			"type": "bool",
			"name": translates["Emulates_Old_Console"],
			"explanation": translates["0x0006"]
		},

		"Language": {
			"type": "select",
			"args": (
				[
					("English", "en"),
					("Chinese", "zh")
				],
				True
			),
			"name": translates["Language"],
			"explanation": translates["0x0005"]
		},

		"ShowSupportMode": {
			"type": "bool",
			"name": translates["Show_Support_Mode"],
			"explanation": translates["0x000B"]
		},

		"BackgroundColor": {
			"type": "color",
			"name": translates["Background_Color"],
			"explanation": translates["Background_Color"]
		},

		"ForegroundColor": {
			"type": "color",
			"name": translates["Text_Color"],
			"explanation": translates["Text_Display_Color"]
		},

		"SelectedColor": {
			"type": "color",
			"name": translates["Select_Color"],
			"explanation": translates["Select_Color"]
		}
	},

	"About": {
		"__cfg__": {
			"name": translates["About"],
			"isSetting": False
		},

		"text": translates["0x0004"]
	},

	"Help": {
		"__cfg__": {
			"name": translates["Help"],
			"isSetting": False
		},

		"text": translates["0x0003"]
	}
}


def loadColorSetting():
	curses.init_pair(SELECTED_COLOR, config["GUISettings"]["SelectedColor"], config["GUISettings"]["BackgroundColor"])

	curses.init_pair(
		BACKGROUND_COLOR,
		config["GUISettings"]["BackgroundColor"],
		config["GUISettings"]["BackgroundColor"]
	)
	curses.init_pair(TEXT_COLOR, config["GUISettings"]["ForegroundColor"], config["GUISettings"]["BackgroundColor"])

	scr.bkgd(curses.color_pair(TEXT_COLOR))


def flush():
	global selectedConfig, maxConfigSize, enterPress, config

	clearZone(1, 3, windowSizeX - EXPLANATION_SIZE, windowSizeY - 2)

	lang = config["GUISettings"]["Language"]

	tabDisplayStart = True
	tabPosition = 0
	for index, (tabName, value) in enumerate(settingMappingTable.items()):
		tabConfig = value["__cfg__"]

		tabName_ = tabConfig["name"][lang]

		color = curses.color_pair(0)

		if index == selectedTab:
			color = curses.color_pair(SELECTED_COLOR)

		addstr(0, tabPosition + 1 + len_(tabName_), "┬")

		if tabDisplayStart:
			addstr(1, tabPosition + 2, tabName_, color)
		else:
			addstr(1, tabPosition + 1, tabName_, color)

		addstr(1, tabPosition + 1 + len_(tabName_), "│")
		addstr(2, tabPosition + 1 + len_(tabName_), "┴")

		tabPosition += len_(tabName_) + 2

		tabDisplayStart = False

		if selectedTab == index:
			if tabConfig["isSetting"]:
				maxConfigSize = len(value) - 2

				configPosition = 3

				for index1, (configName, value1) in enumerate(value.items()):
					if configName != "__cfg__":
						configDisplayName = value1["name"][lang]
						configValue = config[tabName][configName]
						configValueDisplay = subTextSize(str(configValue), MAX_DISPLAY_VALUE_SIZE).replace("'", "")

						color = curses.color_pair(0)
						displayText = ""

						if selectedConfig == index1 - 1:
							if enterPress:
								enterPress = False

								if value1["type"] in changeValueFunctions:
									if "args" in value1:
										configValue = changeValueFunctions[value1["type"]](
											configValue, lang,
											*value1["args"]
										)
									else:
										configValue = changeValueFunctions[value1["type"]](configValue, lang)

									config[tabName][configName] = configValue
									configValueDisplay = subTextSize(str(configValue), MAX_DISPLAY_VALUE_SIZE).replace(
										"'", "")

									saveConfig()
									loadColorSetting()

									flush()

							color = curses.color_pair(SELECTED_COLOR)

							displayText = subText(value1["explanation"][lang], EXPLANATION_SIZE - 3)

							clearZone(windowSizeX - EXPLANATION_SIZE + 2, 3, windowSizeX - 1, windowSizeY - 2)

						addstr(configPosition, 2, configDisplayName, color)

						addstr(
							configPosition,
							windowSizeX - EXPLANATION_SIZE - len_(configValueDisplay),
							configValueDisplay,
							color
						)

						index = 3
						for t in displayText:
							addstr(index, windowSizeX - EXPLANATION_SIZE + 2, t)

							index += 1

						configPosition += 1
			else:
				clearZone(windowSizeX - EXPLANATION_SIZE + 2, 3, windowSizeX - 1, windowSizeY - 2)

				if "text" in value:
					text = value["text"][lang].split("\n")
					if "__nobreak__" not in value:
						text = subText(value["text"][lang], size=windowSizeX - EXPLANATION_SIZE - 2)

					index = 3
					for t in text:
						addstr(index, 2, t)

						index += 1
				elif "call" in value:
					globals()[value["call"]](lang)


def initGui(sizeX=None, sizeY=None, mainMode=True):
	if sizeX is None and sizeY is None:
		sizeY, sizeX = scr.getmaxyx()

	scr.clear()
	scr.box()

	addXLine(2)

	addYLine(sizeX - EXPLANATION_SIZE, y=2)

	addstr(1, sizeX - len(VERSION) - 1, VERSION)

	if mainMode:
		flush()


def initEvent():
	def windowSizeChangeEventMain():
		global windowSizeX, windowSizeY

		lastWindowSizeX = 0
		lastWindowSizeY = 0

		while True:
			sizeY, sizeX = scr.getmaxyx()

			if sizeX != lastWindowSizeX or sizeY != lastWindowSizeY:
				lastWindowSizeX = sizeX
				lastWindowSizeY = sizeY

				windowSizeX = sizeX
				windowSizeY = sizeY

				for callback in windowSizeChangeEvent:
					thread = threading.Thread(target=callback, args=(sizeX, sizeY))
					thread.setDaemon(True)
					thread.start()

			scr.resize(sizeY, sizeX)

			time.sleep(0.01)

	needRunEvent = [
		windowSizeChangeEventMain
	]

	for func in needRunEvent:
		thread = threading.Thread(target=func)
		thread.setDaemon(True)
		thread.start()


def main():
	global selectedTab, selectedConfig, enterPress, upKeyPress, downKeyPress, mainMenuSelected

	loadConfig()
	loadColorSetting()

	curses.curs_set(False)
	scr.box()

	windowSizeChangeEvent.append(initGui)

	initGui(mainMode=False)
	initEvent()

	flush()

	while True:
		keycode = scr.getch()

		if keycode == ord("	") or keycode == ord("d") or keycode == curses.KEY_RIGHT:  # TAB
			if selectedTab < len(settingMappingTable) - 1:
				selectedTab += 1
			else:
				selectedTab = 0

			selectedConfig = 0
			mainMenuSelected = 0

		elif keycode == curses.KEY_BTAB or keycode == ord("a") or keycode == curses.KEY_LEFT:
			if selectedTab > 0:
				selectedTab -= 1
			else:
				selectedTab = len(settingMappingTable) - 1

			selectedConfig = 0
			mainMenuSelected = 0

		elif keycode == ord("w") or keycode == curses.KEY_UP:
			upKeyPress = True

			if selectedConfig > 0:
				selectedConfig -= 1

		elif keycode == ord("s") or keycode == curses.KEY_DOWN:
			downKeyPress = True

			if selectedConfig < maxConfigSize:
				selectedConfig += 1

		elif keycode == 10:
			enterPress = True

		elif keycode == ord("q"):
			endwin()

			return 0

		flush()


if __name__ == "__main__":
	try:
		main()
	except Exception as error:
		endwin()
