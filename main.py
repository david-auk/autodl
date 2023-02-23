import os
import urllib.parse
import requests

# Checking and writing Telegram API token
if os.path.isfile("./telegram-token.txt") is False:
	print("Telegram token not found..\n\nN/A for none.")
	token = input("Telegram Token:\t\t")
	if token == "N/A":
		open("./telegram-token.txt", 'a').close()
	else:
		tgFile = open("./telegram-token.txt", "w")
		tgFile.write(token)
		tgFile.close

# Checking and writing user(s) ChatID
if os.path.isfile("./user-token.txt") is False:
	print("User ChatID not found..\n\nN/A for none.")
	hostChatId = input("Host ChatID:\t\t")
	if hostChatId == "N/A":
		open("./user-token.txt", 'a').close()
	else:	
		print("Seperate with ',' (enter for none)")
		aditionalChatId = input("Aditional ChatID:\t")
		if aditionalChatId:
			aditionalChatId = aditionalChatId.replace(",", "\n")
			chatIdTotaal = hostChatId + "\n" + aditionalChatId
		else:
			chatIdTotaal = hostChatId

		chatIdFile = open("./user-token.txt", "w")
		chatIdFile.write(chatIdTotaal)
		chatIdFile.close

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

# Function for adding to DB