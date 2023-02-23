import os
import urllib.parse
import requests

# Checking and writing Telegram API token
if os.path.isfile("./telegram-token.txt") is False:
	print("Telegram token not found..\n\nWrite N/A for none.")
	token = input("Telegram Token: ")
	if token == "N/A":
		open("./telegram-token.txt", 'a').close()
	else:
		tgFile = open("./telegram-token.txt", "w")
		tgFile.write(token)
		tgFile.close

# Function for messaging host using query
def msgHost(query):
	telegramToken = open("telegram-token.txt").read()
	formatedQuote = urllib.parse.quote(query)
	hostToken = open("user-token.txt").readline().strip('\n')
	requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,hostToken,formatedQuote))

# Function for messaging all using query
def msgAll(query):
	telegramToken = open("telegram-token.txt").read()
	formatedQuote = urllib.parse.quote(query)
	usersToken = open("user-token.txt").read()
	with open('user-token.txt') as usersToken:
		for currentUserToken in usersToken:
			currentUserToken = currentUserToken.strip()
			requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,currentUserToken,formatedQuote))
