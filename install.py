import os
import mysql.connector as database
import json
import getpass

# Defining the dictionary structure
mariadb = {
	'credentials': {
		'user': "",
		'password': "",
	},
	'connection': {
		'host': "",
		'database': ""
	}
}

telegram = {
	'credentials': {
		'token': ''
	},
	'chatid': {
		'hostChatId': '',
		'adminChatId': [],
		'userChatId': []
	}
}

for key in mariadb:
	for sub_key in mariadb[key]:
		if sub_key == 'password':
			mariadb[key][sub_key] = getpass.getpass(prompt=f"DB {sub_key}: ")
		else:
			mariadb[key][sub_key] = input(f"DB {sub_key}: ")

for key in telegram:
	if key == 'credentials':
		for sub_key in telegram[key]:
			telegram[key][sub_key] = getpass.getpass(prompt=f"Telegram {sub_key}: ")
	else:
		for sub_key in telegram[key]:
			if sub_key == 'hostChatId':
				telegram[key][sub_key] = input(f"Telegram {sub_key}: ")	
			else:
				value = input(f"Telegram (seperate w/ ',') {sub_key}: ")
				if ',' in value:
					telegram[key][sub_key] = value.split(',')
				else:
					telegram[key][sub_key] = value

# Write the resulting dictionary to a secret.py file
with open('secret.py', 'w') as file:
	file.write("mariadb = " + json.dumps(mariadb, indent=4).replace('"', "'").replace("    ","\t") + "\n")
	file.write("telegram = " + json.dumps(telegram, indent=4).replace('"', "'").replace("    ","\t"))

import secret

mydb = database.connect(
	host=secret.mariadb['connection']['host'],
	user=secret.mariadb['credentials']['user'],
	password=secret.mariadb['credentials']['password'],
	database=secret.mariadb['connection']['database']
)

myCursor = mydb.cursor()
myCursor.execute("SHOW TABLES")
accountExists = False
contentExists = False
for x in myCursor:
	if "account" in x:
		accountExists = True
	if "content" in x:
		contentExists = True
if accountExists is False:
	try:
		myCursor.execute("CREATE TABLE account (title text, id CHAR(25), priority int)")
		print(myCursor.rowcount, "TABLES added.")
	except database.Error as e:
		print(f"Error creating table in {mydb.database}: {e}")

if contentExists is False:
	try:
		myCursor.execute("CREATE TABLE content (title text, childfrom text, id CHAR(12), videopath text, thumbnailpath text, deleted int, deletedtype text, downloaddate text)")
		print(myCursor.rowcount, "TABLES added.")
	except database.Error as e:
		print(f"Error creating table in {mydb.database}: {e}")

myCursor.close()