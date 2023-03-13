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
myCursorContentRequest = functions.getData('content', 'id', '=', 'ALL')
for (title, childfrom, id, videopath, extention, deleted, deleteddate, deletedtype, requestuser, uploaddate) in myCursorContentRequest:
	isAvalible, avalibilityType, striker = functions.avalibilityCheck(id)

	currentRequestNum += 1

	count = len(f'{currentRequestNum}/{totalRows}') + len(f'{100/totalRows*currentRequestNum:.2f}%')
	terminalWidth = (originalTerminalWidth - count)

	print(f"{functions.coloursB['white']}{100/totalRows*currentRequestNum:.2f}%{functions.colours['reset']}\033[{terminalWidth}C{currentRequestNum}/{totalRows}", end = '\r')

	if isAvalible is False:
		if avalibilityType == 'Deleted' or avalibilityType == 'Private':
			print(f"{functions.coloursB['red']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {childfrom} | {title}")
		else:
			if avalibilityType == 'Unlisted' or avalibilityType == 'Striked':
				print(f"{functions.coloursB['yellow']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {childfrom} | {title}")	

		if deleted == 0: # He just got deleted
			print(f'  ^ The first time detecting this as {avalibilityType}\n')
			functions.chData('content', id, 'deleted', 1)
			functions.chData('content', id, 'deletedtype', avalibilityType)
			functions.chData('content', id, 'deleteddate', formattedDate)
			if avalibilityType == 'Private':
				functions.msgAll(f"{title} from \'{childfrom}\' just got Privated, not Deleted ")
			else:
				if avalibilityType == 'Deleted':
					functions.msgAll(f"{title} from \'{childfrom}\' just got Deleted, not Privated")
				else:
					if avalibilityType == 'Unlisted':
						functions.msgAll(f"{title} from \'{childfrom}\' just got Unlisted \nhttps://www.youtube.com/watch?v={id}")
					else:
						if avalibilityType == 'Striked':
							functions.msgAll(f"{title} from \'{childfrom}\' just got Striked by {striker}.")

	# If the content is avalible
	else:
		if deleted == 1: # He just got back online
			print(f"{functions.coloursB['green']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {childfrom} | {title}")
			print(f'  ^ The first time detecting this as {avalibilityType} (Again)\n')
			functions.chData('content', id, 'deleted', 0)
			functions.chData('content', id, 'deletedtype', 'public')
			functions.chData('content', id, 'deleteddate', formattedDate)
			functions.msgAll(f"{title}. from \'{childfrom}\' just got put back Online from {deletedtype}\nhttps://www.youtube.com/watch?v={id}")