import functions
import shutil
import datetime
import threading
import time

runInBackround = True
sleepTime = 0.03

originalTerminalWidth = shutil.get_terminal_size().columns

# Getting date
currentDate = datetime.datetime.now()
formattedDate = currentDate.strftime("%d-%m-%Y")

totalRows = functions.countData("content", 'ALL')

def checkingAndInforming(title, id, childfrom, nr, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser):
	isAvalible, avalibilityType, striker = functions.availabilityCheck(id)
	if isAvalible is False:
		if avalibilityType == 'Deleted' or avalibilityType == 'Private':
			print(f"{functions.coloursB['red']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {childfrom} | {title}")
		else:
			if avalibilityType == 'Unlisted' or avalibilityType == 'Striked':
				print(f"{functions.coloursB['yellow']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {childfrom} | {title}")	

		if deleted == 0: # Video status just got deleted
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
							functions.msgAll(f"{title} from \'{childfrom}\' just got Striked by \'{striker}\'")
	# If the content is avalible
	else:
		if deleted == 1: # Video status just got back online
			print(f"{functions.coloursB['green']}{avalibilityType.upper()}{functions.colours['reset']} - {id} | {childfrom} | {title}")
			print(f'  ^ The first time detecting this as {avalibilityType} (Again)\n')
			functions.chData('content', id, 'deleted', 0)
			functions.chData('content', id, 'deletedtype', 'public')
			functions.chData('content', id, 'deleteddate', formattedDate)
			functions.msgAll(f"{title}. from \'{childfrom}\' just got put back Online from {deletedtype}\nhttps://www.youtube.com/watch?v={id}")

threads = []
currentRequestNum = 0
for (title, id, childfrom, nr, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser) in functions.getData('content', 'ORDER BY deleted DESC'):

 	currentRequestNum += 1

 	count = len(f'{currentRequestNum}/{totalRows}') + len(f'{100/totalRows*currentRequestNum:.2f}%')
 	terminalWidth = (originalTerminalWidth - count)

 	print(f"{functions.coloursB['white']}{100/totalRows*currentRequestNum:.2f}%{functions.colours['reset']}\033[{terminalWidth}C{currentRequestNum}/{totalRows}", end = '\r')

 	if runInBackround is True:
 		t = threading.Thread(target=checkingAndInforming, args=(title, id, childfrom, nr, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser))
 		threads.append(t)
 		t.start()
 		time.sleep(0.03)
 	elif runInBackround is False:
 		checkingAndInforming(title, id, childfrom, nr, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser)
 	else:
 		print("Please enter a 'runInBackround' value")
 		break

if runInBackround:
	currentRequestNum = 0
	for t in threads:
		currentRequestNum += 1
		count = len(f'Cleaning up sessions') + len(f'{currentRequestNum}/{totalRows}')
		terminalWidth = (originalTerminalWidth - count)
		print(f"Cleaning up sessions\033[{terminalWidth}C{currentRequestNum}/{totalRows}", end = '\r')
		time.sleep(0.001)
		t.join()