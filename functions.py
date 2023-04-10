import mysql.connector as database
import urllib.request
import urllib.parse
import requests
import secret
import datetime
import subprocess
import shutil
import time
import os
import re

from telegram import Bot, ParseMode
from yt_dlp import YoutubeDL, utils
from mysql.connector import conversion


# Define coulors
colours = {
	'red': "\033[0;31m",
	'green': "\033[0;32m",
	'yellow': "\033[0;33m",
	'blue': "\033[0;34m",
	'magenta': "\033[0;35m",
	'cyan': "\033[0;36m",
	'white': "\033[0;37m",
	'reset': "\033[0m",
}

# Define bold coulors
coloursB = {
	'red': "\033[1;31m",
	'green': "\033[1;32m",
	'yellow': "\033[1;33m",
	'blue': "\033[1;34m",
	'magenta': "\033[1;35m",
	'cyan': "\033[1;36m",
	'white': "\033[1;37m",
}

# Getting color related to priority
def colourPriority(priority):
	if priority == 1:
		priorityColor = coloursB['green']
	else:
		if priority == 2:
			priorityColor = coloursB['yellow']
		else:
			if priority == 3:
				priorityColor = coloursB['red']
	return priorityColor

# Defining DB configuration
mydb = database.connect(
	host=secret.mariadb['connection']['host'],
	user=secret.mariadb['credentials']['user'],
	password=secret.mariadb['credentials']['password'],
	database=secret.mariadb['connection']['database'],
	converter_class=conversion.MySQLConverter
)

class MyLoggerQuiet(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		pass

# Function for adding instances to the account table
def addAccountData(title, channelid, priority):
	mydb.reconnect()
	addAccountDataCursor = mydb.cursor(buffered=True)
	try:
		table = 'account'
		statement = f"INSERT INTO {table} VALUES (\"{title}\", \"{channelid}\", \"{priority}\", \"N/A\")"
		print(statement)
		addAccountDataCursor.execute(statement)
		mydb.commit()
		#print(addAccountDataCursor.rowcount, "record inserted.")
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for adding instances to the content table
def addChatIdData(name, id, priority, authenticated):
	mydb.reconnect()
	addChatIdDataCursor = mydb.cursor(buffered=True)
	try:
		table = 'chatid'
		statement = f"INSERT INTO {table} VALUES (\"{mydb.converter.escape(name)}\", \"{id}\", \"{priority}\", \"{authenticated}\")"
		addChatIdDataCursor.execute(statement)
		mydb.commit()
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for adding instances to the content table
def addContentData(title, id, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser):
	mydb.reconnect()
	addContentDataCursor = mydb.cursor(buffered=True)
	try:
		table = 'content'						#  title, 								id, 							childfrom,							     videopath, 	   extention, 	  subtitles,	 	 uploaddate,	 	    downloaddate, 	   		 deleteddate,	   	   deleted,	     deletedtype, 	    requestuser
		statement = f"INSERT INTO {table} VALUES (\"{mydb.converter.escape(title)}\", \"{id}\", \"{mydb.converter.escape(childfrom)}\", \"{mydb.converter.escape(videopath)}\", \"{extention}\", {subtitles}, \"{int(uploaddate)}\", \"{int(downloaddate)}\", \"{int(deleteddate)}\", {int(deleted)}, \"{deletedtype}\", \"{requestuser}\")"
		addContentDataCursor.execute(statement)
		mydb.commit()
		return addContentDataCursor.rowcount
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for searching DB
def getData(table, inputstatement):
	mydb.reconnect()
	getDataCursor = mydb.cursor(buffered=True)
	try:
		if inputstatement == "ALL":
			statement = "SELECT * FROM " + table
		else:
			statement = f"SELECT * FROM {table} {inputstatement}" # WHERE {column} {operator} \"{instanceid}\""
		getDataCursor.execute(statement)
		return getDataCursor
	except database.Error as e:
		print(f"Error retrieving entry from {mydb.database}[{table}]: {e}")

# Function for changing data of a table
def chData(table, id, column, newData):
	mydb.reconnect()
	chDataCursor = mydb.cursor(buffered=True)
	try:
		statement = "UPDATE " + table + " SET {}=\"{}\" WHERE id=\"{}\"".format(column,mydb.converter.escape(newData),id)
		chDataCursor.execute(statement)
		mydb.commit()
	except database.Error as e:
		print(f"Error manipulating data from {mydb.database}[{table}]: {e}")

# Function for counting data of a table
def countData(table, inputstatement):
	mydb.reconnect()
	countDataCursor = mydb.cursor(buffered=True)
	column = 'id'
	if inputstatement == 'ALL':
		#statement = f'SELECT COUNT(ALL {column}) FROM {table}'
		statement = f'SELECT COUNT(*) FROM {table}'
	else:
		#statement = f'SELECT COUNT(ALL {column}) FROM {table} {inputstatement}'
		statement = f'SELECT COUNT(*) FROM {table} {inputstatement}'

	countDataCursor.execute(statement)
	for x in countDataCursor:
		count = x[0]
	return count

def getMaxDataValue(table, column):
	mydb.reconnect()
	getMaxDataValueCursor = mydb.cursor(buffered=True)
	statement = f'SELECT MAX({column}) FROM {table};'
	getMaxDataValueCursor.execute(statement)
	for x in getMaxDataValueCursor:
		maxValue = x[0]
	return maxValue

# Function for deleting rows in any table using the id variable
def delData(table, instanceid):
	mydb.reconnect()
	delDataCursor = mydb.cursor(buffered=True)
	try:
		statement = "DELETE FROM " + table + " WHERE id=\'{}\'".format(instanceid)
		delDataCursor.execute(statement)
		mydb.commit()
		if delDataCursor.rowcount == 0:
			print("No rows where deleted.")
	except database.Error as e:
		print(f"Error deleting entry from {mydb.database}[{table}]: {e}")

# Function for deleting video
def delVid(vidId):
	
	# Getting facts
	rootDownloadDir = secret.configuration['general']['backupDir']
	for (title, id, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, writtenrequestuser) in getData('content', f'WHERE id=\"{vidId}\"'):
		accountPath = f'{rootDownloadDir}/{childfrom}'
		pathDictionary = {
			'video': f'{rootDownloadDir}/{childfrom}/{videopath}.{extention}',
			'thumbnail': f'{rootDownloadDir}/{childfrom}/thumbnail/{videopath}.jpg',
			'description': f'{rootDownloadDir}/{childfrom}/description/{videopath}.txt'
		}

	# Removing files
	for value in pathDictionary:
		os.remove(pathDictionary[value])

	# Getting all content in directory
	dirContent = os.listdir(accountPath)
	dirContent = [f for f in dirContent if not f.startswith('.')]
	dirContent.remove('thumbnail')
	dirContent.remove('description')

	# Deleting directory (if empty)
	if not dirContent:
		shutil.rmtree(f'{rootDownloadDir}/{childfrom}')

	# Deleting entry from DB
	delData('content', vidId)

def uploadFile(title, description, path):
	url = 'https://file.io/'
	headers = {
		'accept': 'application/json'
	}
	data = {
		'title': title,
		'description': description,
		'maxDownloads': '1',
		'autoDelete': 'true'
	}
	files = {
		'file': (path, open(path, 'rb'), 'multipart/form-data')
	}
	response = requests.post(url, headers=headers, data=data, files=files)

	return response.json()['link']

def escapeMarkdown(text):
	escape_list = ['*', '_', '`']
	formatedQuote = ''.join(['\\'+c if c in escape_list else c for c in text])
	return formatedQuote

def escapeMarkdownAll(text):
	escape_list = ['>', '-', ']', '[', '.', '}', '{', '|', ')', '(', '#', '!', '=', '+', '*', '_', '`']
	formatedQuote = ''.join(['\\'+c if c in escape_list else c for c in text])
	return formatedQuote

# Function that messages the 'Host' using credentials from secret.py
def msgHost(query, usingMarkdown):
	telegramToken = secret.telegram['credentials']['token']
	for x in getData("chatid", 'WHERE priority=\"1\"'):
		hostChatId = x[1]

	if usingMarkdown:
		escape_list = ['>', '-', ']', '[', '.', '}', '{', '|', ')', '(', '#', '!', '=', '+']
		formatedQuote = ''.join(['\\'+c if c in escape_list else c for c in query])
		Bot(token=secret.telegram['credentials']['token']).send_message(chat_id=hostChatId, text=formatedQuote, parse_mode=ParseMode.MARKDOWN_V2)
	else:
		formatedQuote = urllib.parse.quote(query)
		requests.get(f"https://api.telegram.org/bot{telegramToken}/sendMessage?chat_id={hostChatId}&text={formatedQuote}")

# Function that messages every chatid from secret.py
def msgAll(query, usingMarkdown):
	telegramToken = secret.telegram['credentials']['token']
	if usingMarkdown:
		escape_list = ['>', '-', ']', '[', '.', '}', '{', '|', ')', '(', '#', '!', '=', '+']
		formatedQuote = ''.join(['\\'+c if c in escape_list else c for c in query])
		for x in getData("chatid", 'ALL'):
			currentUserChatId = x[1]
			Bot(token=secret.telegram['credentials']['token']).send_message(chat_id=currentUserChatId, text=formatedQuote, parse_mode=ParseMode.MARKDOWN_V2)
	else:
		formatedQuote = urllib.parse.quote(query)
		for x in getData("chatid", 'ALL'):
			currentUserChatId = x[1]
			requests.get(f"https://api.telegram.org/bot{telegramToken}/sendMessage?chat_id={currentUserChatId}&text={formatedQuote}")

# Function for downloading video
def downloadVid(vidId, channelTitle, filename):
	rootDownloadDir = secret.configuration['general']['backupDir']
	ydl_opts = {
		'outtmpl': f'{rootDownloadDir}/{channelTitle}/{filename}',
		'subtitleslangs': ['all', '-live_chat'],
		'writesubtitles': True,
		'format': 'bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio',
		'postprocessors': [{
			'key': 'FFmpegEmbedSubtitle'
		}]
	}
	success = False
	tries = 0
	while not success:
		try:
			if tries == 5:
				break 
			with YoutubeDL(ydl_opts) as ydl:
				ydl.download([f'https://www.youtube.com/watch?v={vidId}'])
			success = True
			errorType = True
		except Exception as e:
			print(f"Download failed: {e}")
			errorType = e
			tries += 1
	return success, errorType

# Function for saving thumbnail
def downloadThumbnail(vidId, channelTitle, filename, secondLink):
	rootDownloadDir = secret.configuration['general']['backupDir']
	destinationDir = f'{rootDownloadDir}/{channelTitle}/thumbnail'

	# Check if path exists, if not create directory
	if not os.path.exists(destinationDir):
		os.makedirs(destinationDir)

	url = f'https://img.youtube.com/vi/{vidId}/maxresdefault.jpg'
	filename = f'{destinationDir}/{filename}.jpg'

	success = False

	tries = 0
	while not success:
		try:
			if tries == 3:
				break 
			urllib.request.urlretrieve(url, filename)	# Downloading the url
			print(f"{coloursB['green']}√{colours['reset']} MAX quality thumbnail")
			success = True
		except Exception as e:
			print(f"{coloursB['red']}X{colours['reset']} MAX quality thumbnail")
			tries += 1

	if success:
		return success

	url = secondLink

	tries = 0
	while not success:
		try:
			if tries == 5:
				break 
			urllib.request.urlretrieve(url, filename)	# Downloading the url
			print(f"{coloursB['yellow']}√{colours['reset']} Generic quality thumbnail")
			success = True
		except Exception as e:
			print(f"{coloursB['red']}X{colours['reset']} Generic quality thumbnail")
			tries += 1

	if success:
		return success
	else:
		msgHost(f"ERROR: Could not download thumbnail, Account: \'{channelTitle}\", Url: \'https://www.youtube.com/watch?v={vidId}\'", False)
		quit()

# Function for writing description of video
def writeDescription(channelTitle, filename, description):
	rootDownloadDir = secret.configuration['general']['backupDir']
	destinationDir = f'{rootDownloadDir}/{channelTitle}/description'

	# Check if path exists, if not create directory
	if not os.path.exists(destinationDir):
		os.makedirs(destinationDir)

	filename = f'{destinationDir}/{filename}.txt'

	succes = False
	with open(filename, 'w') as f:
		f.write(str(description))
		print(f"{coloursB['green']}√{colours['reset']} description written")
		succes = True

	return succes

# Function for converting non filename friendly srt to filename friendly
def filenameFriendly(srtValue):

	# Lowercase all characters
	srtValue = srtValue.lower()

	# Replace non-alphanumeric characters with underscores
	srtValue = re.sub(r'[^a-zA-Z0-9\-]+', '_', srtValue)

	# Remove any leading Underscores
	srtValue = re.sub(r'^_+', '', srtValue)

	# Remove any trailing Underscores
	srtValue = srtValue.rstrip('_')

	# Cut the resulting filename to a maximum length of 255 bytes
	filename = srtValue[:255]
	
	return filename

# For making a dir in rootdownload when a python download request has come in
def accNameFriendly(srtValue):
	# Split the input string into a list of words
	srtValue = srtValue.lower()
	words = srtValue.split()

	# Capitalize the first letter of each word and join them together
	modifiedWords = [word.capitalize() for word in words]
	modifiedString = ''.join(modifiedWords)
	modifiedString = re.sub(r'[^a-zA-Z0-9\-]+', '', modifiedString)

	return modifiedString

# Function for saving facts of a video to a dictionary
def getFacts(vidId):
	rootDownloadDir = secret.configuration['general']['backupDir']
	ydl_opts = {
		'outtmpl': f'{rootDownloadDir}/accountdir/filename',
		'subtitleslangs': ['all', '-live_chat'],
		'writesubtitles': True,
		'embedsubtitles': True,
		'format': 'bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio',
		'quiet': True
	}

	success = False
	tries = 0
	while not success:
		try:
			if tries == 3:
				break 
			with YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(f'https://www.youtube.com/watch?v={vidId}', download=False)
			success = True
		except Exception as e:
			tries += 1
			ydl_opts = {
				'outtmpl': f'{rootDownloadDir}/{channelTitle}/filename',
				'subtitleslangs': ['all', '-live_chat'],
				'writesubtitles': True,
				'embedsubtitles': True,
				'quiet': True
			}
	if success is False:
		info = 'N/A'

	return success, info

def humanReadableSize(path):
	# Get the size of the file in bytes
	file_size = os.path.getsize(path)

	# Convert to a human-readable format
	size_suffixes = ['B', 'KB', 'MB', 'GB', 'TB']  # List of size suffixes
	size_suffix_index = 0  # Initialize index of the size suffix

	while file_size > 1024 and size_suffix_index < len(size_suffixes)-1:
		file_size /= 1024
		size_suffix_index += 1

	human_readable_size = f"{file_size:.2f} {size_suffixes[size_suffix_index]}"

	return human_readable_size

def getChannelFacts(link):
	link = f"https://youtube.com/channel/{link}"
	ydl_opts = {
		'skip_download': True,
		'quiet': True,
		'no_warnings': True,
		'playlist_items': '1',
		'match_filter': 'channel',
		'extract_flat': True,
		'logger': MyLoggerQuiet()
	}
	with YoutubeDL(ydl_opts) as ydl:
		try:
			ydl.extract_info(link, download=False)
			return False
		except utils.DownloadError as e:
			message = e
			if "This channel has no uploads" in str(e):
				message = "no_uploads"
			elif "This account has been terminated" in str(e):
				message = "terminated"
			return message
		else:
			return "else"

def getDate(date):
	year = date[:4]
	month = date[4:6]
	day = date[6:8]
	if date[8:]:
		hour = date[8:10]
		minute = date[10:12]
	else:
		hour, minute = '00', '00'
	return (day, month, year, hour, minute)

def isYtLink(link):
	"""Extracts the YouTube video ID and type (video or channel) from a URL string."""
	video_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=))([\w\-]{11})(?:\S+)?"
	channel_pattern1 = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:c\/|channel\/)([\w\-]+)(?:\S+)?"
	channel_pattern2 = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/@([\w\-]+)(?:\S+)?"
	channel_pattern3 = r"(?:https?:\/\/)?(?:www\.)?reddit.com\/r\/([\w\-]+)(?:\S+)?"
	
	video_match = re.match(video_pattern, link)
	channel_match1 = re.match(channel_pattern1, link)
	channel_match2 = re.match(channel_pattern2, link)
	channel_match3 = re.match(channel_pattern3, link)
	
	if video_match:
		return (True, "video", video_match.group(1), 'N/A')
	elif channel_match1:
		return (True, "channel", f"channel/{channel_match1.group(1)}", channel_match1.group(1))
	elif channel_match2:
		return (True, "channel", f"@{channel_match2.group(1)}", channel_match2.group(1))
	elif channel_match3:
		return (True, "channel", f"r/{channel_match3.group(1)}", channel_match3.group(1))
	else:
		return (False, 'N/A', 'N/A', 'N/A')

def cleanChannelLink(link):
	"""Extracts the YouTube video ID and type (video or channel) from a URL string."""
	channel_pattern = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:c\/|channel\/)([\w\-]+)(?:\S+)?"

	channel_match = re.match(channel_pattern, link)
	
	return channel_match.group(1)

# Function for getting the id of chosen type
def getChannelId(ytChannelId):
	ydl_opts = {
		'skip_download': True,
		'quiet': True,
		'no_warnings': True,
		'playlist_items': '1',
		'match_filter': 'channel',
		'extract_flat': True,
		'logger': MyLoggerQuiet()
	}
	try:
		with YoutubeDL(ydl_opts) as ydl:
			result = ydl.extract_info(f"https://youtube.com/{ytChannelId}", download=False)
			if result:
				return True, result.get('channel_id')
	except Exception as e:
		return False, 'N/A'
		

# 
def subCheck(channelTitle, filename, ext):
	rootDownloadDir = secret.configuration['general']['backupDir']
	filename = f"{rootDownloadDir}/{channelTitle}/{filename}.{ext}"

	# Run ffprobe command to get information about the video file
	ffprobe_output = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "default=noprint_wrappers=1:nokey=1", filename])

	has_subtitles = False
	for stream in ffprobe_output.decode().split("\n"):
		if stream.strip() == "subtitle":
			has_subtitles = True
			break

	return has_subtitles

# Function for checking if the vidId is still online
def availabilityCheck(vidId):

	# Create full link
	url = f'https://www.youtube.com/watch?v={vidId}'

	# Make a request to the video page
	response = requests.get(url)
	responseText = response.content.decode('utf-8')

	# Defining default values
	isAvalible = True
	avalibilityType = "Public"
	striker = 'N/A'

	# Checking for certain html values
	if '"playabilityStatus":{"status":"LOGIN_REQUIRED","messages"' in responseText:
		isAvalible = False
		avalibilityType = "Private"
	else:
		if '"playabilityStatus":{"status":"ERROR","reason":"' in responseText:
			isAvalible = False
			for line in responseText.split("\n"):
				if '"playabilityStatus":{"status":"ERROR","reason":"' in line:
					result = re.search(r'(?<=},{"text":")(.*?)(?="})', line)
					if result:
						striker = result.group(1)
						avalibilityType = "Striked"
					else:
						avalibilityType = "Deleted"
					break
		else:
			if '><meta itemprop="unlisted" content="True">' in responseText:
				isAvalible = False
				avalibilityType = "Unlisted"

	return isAvalible, avalibilityType, striker