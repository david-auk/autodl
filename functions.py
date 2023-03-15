import mysql.connector as database
import urllib.request
import urllib.parse
import requests
import secret
import datetime
import subprocess
import os
import re

from yt_dlp import YoutubeDL

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
	database=secret.mariadb['connection']['database']
)

# Function for adding instances to the account table
def addAccountData(title, channelid, priority):
	addAccountDataCursor = mydb.cursor(buffered=True)
	try:
		table = 'account'
		statement = "INSERT INTO account VALUES (\"{}\", \"{}\", \"{}\")".format(title,channelid,priority)
		addAccountDataCursor.execute(statement)
		mydb.commit()
		#print(addAccountDataCursor.rowcount, "record inserted.")
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for adding instances to the content table
def addChatIdData(name, id, priority, authenticated):
	addChatIdDataCursor = mydb.cursor(buffered=True)
	try:
		table = 'chatid'
		statement = f"INSERT INTO {table} VALUES (\"{mydb.converter.escape(name)}\", \"{id}\", \"{priority}\", \"{authenticated}\")"
		addChatIdDataCursor.execute(statement)
		mydb.commit()
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for adding instances to the content table
def addContentData(title, childfrom, id, videopath, extention, subtitles, deleted, deleteddate, deletedtype, requestuser, uploaddate):
	addContentDataCursor = mydb.cursor(buffered=True)
	try:
		table = 'content'
		statement = f"INSERT INTO content VALUES (\"{mydb.converter.escape(title)}\", \"{mydb.converter.escape(childfrom)}\", \"{id}\", \"{mydb.converter.escape(videopath)}\", \"{extention}\", {subtitles}, {deleted}, \"{deleteddate}\", \"{deletedtype}\", \"{requestuser}\", \"{uploaddate}\")"
		addContentDataCursor.execute(statement)
		mydb.commit()
		return addContentDataCursor.rowcount
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for deleting rows in any table using the id variable
def delData(table, instanceid):
	delDataCursor = mydb.cursor(buffered=True)
	try:
		statement = "DELETE FROM " + table + " WHERE id=\'{}\'".format(instanceid)
		delDataCursor.execute(statement)
		mydb.commit()
		if delDataCursor.rowcount == 0:
			print("No rows where deleted.")
	except database.Error as e:
		print(f"Error deleting entry from {mydb.database}[{table}]: {e}")

# Function for searching DB
def getData(table, column, operator, instanceid):
	getDataCursor = mydb.cursor(buffered=True)
	try:
		if instanceid == "ALL":
			statement = "SELECT * FROM " + table
		else:
			statement = "SELECT * FROM " + table + " WHERE {} {} \"{}\"".format(column,operator,instanceid)
		getDataCursor.execute(statement)
		return getDataCursor
	except database.Error as e:
		print(f"Error retrieving entry from {mydb.database}[{table}]: {e}")

# Function for changing data of a table
def chData(table, id, column, newData):
	chDataCursor = mydb.cursor(buffered=True)
	try:
		statement = "UPDATE " + table + " SET {}=\"{}\" WHERE id=\"{}\"".format(column,mydb.converter.escape(newData),id)
		chDataCursor.execute(statement)
		mydb.commit()
	except database.Error as e:
		print(f"Error manipulating data from {mydb.database}[{table}]: {e}")

# Function for counting data of a table
def countData(table, column, arg):
	countDataCursor = mydb.cursor(buffered=True)
	if arg == 'ALL':
		statement = f'SELECT COUNT(ALL {column}) FROM {table}'
	else:
		statement = f'SELECT COUNT(ALL {column}) FROM {table} WHERE {column}=\'{arg}\''

	countDataCursor.execute(statement)
	return countDataCursor

# Function that messages the 'Host' using credentials from secret.py
def msgHost(query):
	telegramToken = secret.telegram['credentials']['token']
	formatedQuote = urllib.parse.quote(query)
	for x in getData("chatid", 'priority', '=', '1'):
		hostChatId = x[1]
	requests.get(f"https://api.telegram.org/bot{telegramToken}/sendMessage?chat_id={hostChatId}&text={formatedQuote}")

# Function that messages every chatid from secret.py
def msgAll(query):
	telegramToken = secret.telegram['credentials']['token']
	formatedQuote = urllib.parse.quote(query)
	for x in getData("chatid", 'priority', '=', 'ALL'):
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
			e = success
		except Exception as e:
			print(f"Download failed: {e}")
			tries += 1
		if success:
			if os.path.exists(f"{rootDownloadDir}/{channelTitle}/{filename}*.vst"):
				pass #delete {rootDownloadDir}/{channelTitle}/{filename}*.vst
	return success, e

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
		msgHost(f"ERROR: Could not download thumbnail, Account: \'{channelTitle}\", Url: \'https://www.youtube.com/watch?v={vidId}\'")
		quit()

# Function for writing description of video
def writeDescription(channelTitle, filename, description):
	rootDownloadDir = secret.configuration['general']['backupDir']
	destinationDir = f'{rootDownloadDir}/{channelTitle}/description'

	# Check if path exists, if not create directory
	if not os.path.exists(destinationDir):
		os.makedirs(destinationDir)

	filename = f'{destinationDir}/{filename}.txt'

	with open(filename, 'w') as f:
		f.write(str(description))
		print(f"{coloursB['green']}√{colours['reset']} description written")

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

# Function for saving facts of a video to a dictionary
def getFacts(vidId, channelTitle, filename):
	rootDownloadDir = secret.configuration['general']['backupDir']
	ydl_opts = {
		'outtmpl': f'{rootDownloadDir}/{channelTitle}/{filename}',
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
				'outtmpl': f'{rootDownloadDir}/{channelTitle}/{filename}',
				'subtitleslangs': ['all', '-live_chat'],
				'writesubtitles': True,
				'embedsubtitles': True,
				'quiet': True
			}
	if success is False:
		info = 'N/A'
		uploadDate = 'N/A'
		return success, info, uploadDate
	
	uploadDate = info['upload_date']
	year = uploadDate[:4]
	month = uploadDate[4:6]
	day = uploadDate[6:]
	uploadDate = f"{day}-{month}-{year}"
	return success, info, uploadDate

# Function for getting vidId
def getVidId(link):
	
	# Check if the URL is in the format https://youtu.be/<video_id>
	if 'youtu.be' in link:

		# Extract the video ID from the URL
		video_id = link.split('/')[-1].split('?')[0]
	else:

		# Extract the video ID from the query string of the URL
		query_string = link.split('?')[1]
		params = dict(item.split('=') for item in query_string.split('&'))
		video_id = params['v']
	
	return video_id

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
def avalibilityCheck(vidId):

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

# Function for closing all the cursors at once
def closeCursor():
	chDataCursor.close()
	delDataCursor.close()
	getDataCursor.close()
	countDataCursor.close()
	addChatIdDataCursor.close()
	addContentDataCursor.close()
	addAccountDataCursor.close()
	getDataContentCheckCursor.close()
	addDeletedContentDataCursor.close()
