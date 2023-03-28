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
		'token': '',
		'userpass': ''
	}
}

telegramSql = {
	'chatid': {
		'hostChatId': {
			'id': '',
			'priority' : '1'
		},
		'adminChatId': {
			'id': '',
			'priority' : '2'
		},
		'userChatId': {
			'id': '',
			'priority' : '3'
		}
	}
}

configuration = {
	'general': {
		'backupDir': ''
	}
}

# Defining diffirent tables and types
myTables = {
	'account': {
		'title': {
			'type': 'text'
		},
		'id': {
			'type': 'char(25)'
		},
		'priority': {
			'type': 'int(11)'
		}
		'pullerror' {
			'type': 'int(11)'
		}
	},
	'content': {
		'title': {
			'type': 'text'
		},
		'id': {
			'type': 'char(12)'
		},
		'childfrom': {
			'type': 'text'
		},
		'nr': {
			'type': 'int'
		}
		'videopath': {
			'type': 'text'
		},
		'extention': {
			'type': 'text'
		},
		'subtitles': {
			'type': 'int(11)'
		},
		'uploaddate': {
			'type': 'text'
		},
		'downloaddate': {
			'type': 'text'
		},
		'deleteddate': {
			'type': 'text'
		},
		'deleted': {
			'type': 'int(11)'
		},
		'deletedtype': {
			'type': 'text'
		},
		'requestuser': {
			'type': 'text'
		}
	},
	'chatid': {
		'name': {
			'type': 'text'
		},
		'id': {
			'type': 'char(25)'
		},
		'priority': {
			'type': 'char(5)'
		},
		'authenticated': {
			'type': 'char(5)'
		}
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

for key in telegramSql:
	for sub_key in telegramSql[key]:
		if sub_key == 'hostChatId':
			telegramSql[key][sub_key]['id'] = input(f"Telegram {sub_key}: ")
		else:
			value = input(f"Telegram (seperate w/ ',') {sub_key}: ")
			if ',' in value:
				telegramSql[key][sub_key]['id'] = value.split(',')
			else:
				telegramSql[key][sub_key]['id'] = value

for key in configuration:
	for sub_key in configuration[key]:
		configuration[key][sub_key] = input(f"Config {sub_key}: ")

# Write the resulting dictionary to a secret.py file
with open('secret.py', 'w') as file:
	file.write("mariadb = " + json.dumps(mariadb, indent=4).replace('"', "'").replace("    ","\t") + "\n")
	file.write("telegram = " + json.dumps(telegram, indent=4).replace('"', "'").replace("    ","\t") + "\n")
	file.write("configuration = " + json.dumps(configuration, indent=4).replace('"', "'").replace("    ","\t"))

import secret
import functions

# Defining connection variable
mydb = database.connect(
	host=secret.mariadb['connection']['host'],
	user=secret.mariadb['credentials']['user'],
	password=secret.mariadb['credentials']['password'],
	database=secret.mariadb['connection']['database']
)

myCursor = mydb.cursor()

# Creating list of added tables
myCursor.execute("SHOW TABLES")
existingTables = []
for x in myCursor:
	existingTables.append(x[0])

# Creating (non installed) tables from myTables dictionary
tableAddedCount = 0
for table in myTables:
	if table not in existingTables:
		fieldOutput = ''
		statement = ''

		# Generating arguments for the SQL statement
		for fieldName, fieldInfo in myTables[table].items():
		    fieldOutput += f"{fieldName} {fieldInfo['type']}, "

		# Remove the extra ", " at the end
		fieldOutput = fieldOutput[:-2]

		# Generating SQL statement from variables
		statement = 'CREATE TABLE ' + table + ' (' + fieldOutput + ')'

		# Executing the SQL statement
		myCursor.execute(statement)
		tableAddedCount += 1

print(f"{tableAddedCount} TABLES added.")

for key in telegramSql:
	for sub_key in telegramSql[key]:
		if telegramSql[key][sub_key]['id']:
			if isinstance(telegramSql[key][sub_key]['id'], list):
				for eachSplitValue in telegramSql[key][sub_key]['id']:
					functions.addChatIdData('N/A', eachSplitValue, telegramSql[key][sub_key]['priority'], 'N/A')
			else:
				functions.addChatIdData('N/A', telegramSql[key][sub_key]['id'], telegramSql[key][sub_key]['priority'], 'N/A')

functions.addChatIdDataCursor.close()