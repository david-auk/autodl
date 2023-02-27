import mysql.connector as database
import urllib.parse
import requests
import secret
import datetime
import os
import re

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

# Function that messages the 'Host' using credentials from secret.py
def msgHost(query):
	telegramToken = secret.telegram['credentials']['token']
	formatedQuote = urllib.parse.quote(query)
	hostChatId = secret.telegram['chatid']['hostChatId']
	requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,hostChatId,formatedQuote))

# Function that messages every chatid from secret.py
def msgAll(query):
	telegramToken = secret.telegram['credentials']['token']
	formatedQuote = urllib.parse.quote(query)
	dictionaryCred = secret.telegram['chatid']
	for key in ['hostChatId', 'userChatId', 'adminChatId']:
		value = dictionaryCred[key]
		if isinstance(value, list):
			for item in value:
				if item:
					currentUserChatId = item
					requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,currentUserChatId,formatedQuote))
		else:
			if value:
				currentUserChatId = value
				requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,currentUserChatId,formatedQuote))

# Defining DB configuration
mydb = database.connect(
	host=secret.mariadb['connection']['host'],
	user=secret.mariadb['credentials']['user'],
	password=secret.mariadb['credentials']['password'],
	database=secret.mariadb['connection']['database']
)

# Defining diffirent cursors for diffirent subtasks in functions
chDataCursor = mydb.cursor(buffered=True)
delDataCursor = mydb.cursor(buffered=True)
getDataCursor = mydb.cursor(buffered=True)
getDataInnerCursor = mydb.cursor(buffered=True)
addContentDataCursor = mydb.cursor(buffered=True)
addAccountDataCursor = mydb.cursor(buffered=True)

# Function for adding instances to the account table
def addAccountData(title, channelid, priority):
	try:
		table = 'account'
		statement = "INSERT INTO account VALUES (\"{}\", \"{}\", \"{}\")".format(title,channelid,priority)
		addAccountDataCursor.execute(statement)
		mydb.commit()
		print(addAccountDataCursor.rowcount, "record inserted.")
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for adding instances to the content table
def addContentData(title, childfrom, urlid, videopath, thumbnailpath, deleted, deletedtype, requestuser, uploaddate):
	try:
		table = 'content'
		statement = "INSERT INTO content VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", {}, \"{}\", \"{}\", \"{}\")".format(mydb.converter.escape(title),mydb.converter.escape(childfrom),urlid,mydb.converter.escape(videopath),mydb.converter.escape(thumbnailpath),deleted,deletedtype,requestuser,uploaddate)
		addContentDataCursor.execute(statement)
		mydb.commit()
		print(addContentDataCursor.rowcount, "record inserted.")
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

# Function for deleting rows in any table using the id variable
def delData(table, instanceid):
	try:
		statement = "DELETE FROM " + table + " WHERE id=\'{}\'".format(instanceid)
		delDataCursor.execute(statement)
		mydb.commit()
		if delDataCursor.rowcount == 0:
			print("No rows where deleted.")
		else:
			print(delDataCursor.rowcount, "rows deleted.")
	except database.Error as e:
		print(f"Error deleting entry from {mydb.database}[{table}]: {e}")

# Function for searching DB
def getData(table, column, instanceid):
	try:
		if instanceid == "ALL":
			statement = "SELECT * FROM " + table
		else:
			statement = "SELECT * FROM " + table + " WHERE {}=\"{}\"".format(column,instanceid)
		getDataCursor.execute(statement)
		return getDataCursor

	except database.Error as e:
		print(f"Error retrieving entry from {mydb.database}[{table}]: {e}")

def getDataContentCheck(instanceid):
	try:
		table = 'content'
		column = 'id'
		statement = "SELECT * FROM " + table + " WHERE {}=\"{}\"".format(column,instanceid)
		getDataInnerCursor.execute(statement)
		entryExists = False
		for x in getDataInnerCursor:
			entryExists = True

		return entryExists

	except database.Error as e:
		print(f"Error retrieving entry from {mydb.database}[{table}]: {e}")

def chData(table, id, column, newData):
	try:
		statement = "UPDATE " + table + " SET {}=\"{}\" WHERE id=\"{}\"".format(column,newData,id)
		chDataCursor.execute(statement)
		mydb.commit()
		if chDataCursor.rowcount == 0:
			print("ERROR: no rows updated")
		else:
			print(chDataCursor.rowcount, "rows updated.")
	except database.Error as e:
		print(f"Error manipulating data from {mydb.database}[{table}]: {e}")



def filenameFriendly(srtValue):
	# lowercase all characters
	srtValue = srtValue.lower()
	# replace non-alphanumeric characters with underscores
	srtValue = re.sub(r'[^\w\s-]', '_', srtValue).strip()
	# truncate the resulting filename to a maximum length of 255 bytes
	filename = srtValue[:255]
	# remove any trailing underscores
	filename = filename.rstrip('_')
	return filename




def closeCursor():
	chDataCursor.close()
	delDataCursor.close()
	getDataCursor.close()
	getDataInnerCursor.close()
	addContentDataCursor.close()
	addAccountDataCursor.close()
