import os
import requests
import urllib.parse
import mariadb_credentials
import mysql.connector as database

# Function for messaging host using query
def msgHost(query):
	telegramToken = open("telegram-token.txt").read()
	formatedQuote = urllib.parse.quote(query)
	hostChatId = open("user-token.txt").readline().strip('\n')
	requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,hostChatId,formatedQuote))

# Function for messaging all using query
def msgAll(query):
	telegramToken = open("telegram-token.txt").read()
	formatedQuote = urllib.parse.quote(query)
	usersChatId = open("user-token.txt").read()
	with open('user-token.txt') as usersChatId:
		for currentUserChatId in usersChatId:
			currentUserChatId = currentUserChatId.strip()
			requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,currentUserChatId,formatedQuote))

# Defining DB configuration
mydb = database.connect(
  host=mariadb_credentials.host,
  user=mariadb_credentials.user,
  password=mariadb_credentials.password,
  database=mariadb_credentials.database
)

mycursor = mydb.cursor()

# Function for adding instances to the account table
def addAccountData(title, channelid, priority):
	try:
		statement = "INSERT INTO account VALUES (\"{}\", \"{}\", \"{}\")".format(title,channelid,priority)
		mycursor.execute(statement)
		mydb.commit()
		print(mycursor.rowcount, "record inserted.")
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")

# Function for adding instances to the content table
def addContentData(title, childfrom, urlid, videopath, thumbnailpath, deleted, deletedtype, uploaddate):
	try:
		statement = "INSERT INTO content VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", {}, \"{}\", \"{}\")".format(title,childfrom,urlid,videopath,thumbnailpath,deleted,deletedtype,uploaddate)
		mycursor.execute(statement)
		mydb.commit()
		print(mycursor.rowcount, "record inserted.")
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")

# Function for deleting rows in any table using the id variable
def delData(table, instanceid):
	try:
		statement = "DELETE FROM " + table + " WHERE id=\'{}\'".format(instanceid)
		mycursor.execute(statement)
		mydb.commit()
		if mycursor.rowcount == 0:
			print("No rows where deleted.")
		else:
			print(mycursor.rowcount, "rows deleted.")
	except database.Error as e:
		print(f"Error deleting entry from database: {e}")

# Function for searching DB
def getData(table, instanceid):
	try:
		if instanceid == "ALL":
			statement = "SELECT * FROM " + table
		else:
			statement = "SELECT * FROM " + table + " WHERE id=\"{}\"".format(instanceid)
		mycursor.execute(statement)
		global returnSucces
		returnSucces = False
		for x in mycursor:
			returnSucces = True
			print(f"Successfully retrieved {x}")
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")

# Example:
# addContentData("title", "account", "urlid", "videopath", "thumbnailpath", "0", "deletedtype", "uploaddate")

mydb.close()