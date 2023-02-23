import os
import urllib.parse
import requests
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

# Function for searching DB
connection = database.connect(
    user=mariadb_credentials.user,
    password=mariadb_credentials.password,
    host=mariadb_credentials.host,
    database=mariadb_credentials.database)


print(mariadb_credentials.password)
# Function for adding to DB