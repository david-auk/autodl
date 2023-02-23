import os
import mysql.connector as database

# Checking for DB configuration
if os.path.isfile("./mariadb_credentials.py"):
	import mariadb_credentials
else:
	print(" # Database configuration # ")
	host = input("host (probably localhost): ")
	database = input ("database: ")
	user = input("user: ")
	password = input("password: ")
	config = "user=\"{}\"\npassword=\"{}\"\nhost=\"{}\"\ndatabase=\"{}\"".format(user,password,host,database)
	dbFile = open("./mariadb_credentials.py", "w")
	dbFile.write(config)
	dbFile.close
	quit()

mydb = database.connect(
  host=mariadb_credentials.host,
  user=mariadb_credentials.user,
  password=mariadb_credentials.password,
  database=mariadb_credentials.database
)

mycursor = mydb.cursor()
mycursor.execute("SHOW TABLES")
accountExists = False
contentExists = False
for x in mycursor:
	if "account" in x:
		accountExists = True
	if "content" in x:
		contentExists = True
if accountExists is False:
	mycursor.execute("CREATE TABLE account (title text, channelid CHAR(25), priority int)")
	print("Created account table")
if contentExists is False:
	mycursor.execute("CREATE TABLE content (title text, childfrom text, urlid CHAR(12), videopath text, thumbnailpath text, deleted int, deletedtype text, uploaddate text)")
	print("Created account content")

mycursor.close()

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