import urllib.parse
import requests

query = "Dit is een test!"

telegramToken = open("telegram-token.txt").read()
usersToken = open("user-token.txt").read()
formatedQuote = urllib.parse.quote(query)

requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(telegramToken,usersToken,formatedQuote))