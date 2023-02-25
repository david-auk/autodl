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

# Function for adding to DB
def addData(table, title, childfrom, urlid, videopath, thumbnailpath, deleted, deletedtype, uploaddate):
	try:
		statement = "INSERT INTO " + table + " VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", {}, \"{}\", \"{}\")".format(title,childfrom,urlid,videopath,thumbnailpath,deleted,deletedtype,uploaddate)
		mycursor.execute(statement)
		mydb.commit()
		print(mycursor.rowcount, "record inserted.")
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")

# Function for deleting rows using the urlid variable
def delData(table, urlid):
	try:
		statement = "DELETE FROM " + table + " WHERE urlid=\'{}\'".format(urlid)
		mycursor.execute(statement)
		mydb.commit()
		if mycursor.rowcount == 0:
			print("No rows where deleted.")
		else:
			print(mycursor.rowcount, "rows deleted.")
	except database.Error as e:
		print(f"Error deleting entry from database: {e}")

# Function for searching DB
def getEntry(last_name):
	try:
		statement = "SELECT first_name, last_name FROM employees WHERE last_name=%s"
		data = (last_name,)
		cursor.execute(statement, data)
		for (first_name, last_name) in cursor:
			print(f"Successfully retrieved {first_name}, {last_name}")
	except database.Error as e:
		print(f"Error retrieving entry from database: {e}")

table = "content"
title = "Yo dit is een - lied (prod text)"
account = "account"
urlid = "aaaaa3232"
videopath = "/mnt/backupstick/account/" + title + ".mp4"
thumbnailpath = "/mnt/backupstick/account/thumbnail/" + title + ".mp4"
deleted = 0
deletedtype = "N/A"
uploaddate = "21/02/2023"

addData(table, title, account, urlid, videopath, thumbnailpath, deleted, deletedtype, uploaddate)
#delData("content", urlid)

mydb.close()