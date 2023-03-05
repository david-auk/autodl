import functions
import shutil
import datetime

originalTerminalWidth = shutil.get_terminal_size().columns

# Getting date
currentDate = datetime.datetime.now()
formattedDate = currentDate.strftime("%d-%m-%Y")

totalRows = functions.countData("content", 'id', 'ALL')
for x in totalRows:
	totalRows = x[0]

currentRequestNum = 0
myCursorContentRequest = functions.getData('content', 'id', 'ALL')
for (title, childfrom, id, videopath, extention, deleted, deleteddate, deletedtype, requestuser, downloaddate) in myCursorContentRequest:
	isAvalible, avalibilityType = functions.avalibilityCheck(id)
	
	currentRequestNum += 1

	count = len(f'{currentRequestNum}/{totalRows}') + len(f'{100/totalRows*currentRequestNum:.2f}%')
	terminalWidth = (originalTerminalWidth - count)

	print(f"{functions.coloursB['white']}{100/totalRows*currentRequestNum:.2f}%{functions.colours['reset']}\033[{terminalWidth}C{currentRequestNum}/{totalRows}", end = '\r')

	if isAvalible is False:
		if avalibilityType == 'Deleted' or avalibilityType == 'Private':
			print(f"{functions.coloursB['red']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {title}")
		else:
			if avalibilityType == 'Unlisted':
				print(f"{functions.coloursB['yellow']}Unlisted{functions.colours['reset']} - {id} | {title}")	

		if deleted == 0: # He just got deleted
			print(f'  ^ The first time detecting this as {avalibilityType}\n')
			functions.chData('content', id, 'deleted', 1)
			functions.chData('content', id, 'deletedtype', avalibilityType)
			functions.chData('content', id, 'deleteddate', formattedDate)
	else: # If the content is avalible
		if deleted == 1: # He just got back online
			print(f"{functions.coloursB['green']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {title}")
			print(f'  ^ The first time detecting this as {avalibilityType} (Again)\n')
			functions.chData('content', id, 'deleted', 0)
			functions.chData('content', id, 'deletedtype', 'public')
			functions.chData('content', id, 'deleteddate', formattedDate)