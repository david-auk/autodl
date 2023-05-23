import functions
import shutil
import datetime
import threading
import time
import argparse

# Create the parser object
parser = argparse.ArgumentParser(description='A python script to check the availability of all the download videos')
parser.add_argument('-b', '--background', action='store_true', default=False, help='Run in the background (is more resource heavy)')
parser.add_argument('-t', '--sleeptime', type=float, default=0.1, help='Set how long the wait time before next request, default: 0.01')
args = parser.parse_args()

runInBackround = args.background
sleepTime = args.sleeptime

originalTerminalWidth = shutil.get_terminal_size().columns

totalRows = functions.countData("content", 'ALL')

def checkingAndInforming(title, vidId, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser):
	isAvalible, avalibilityType, striker = functions.availabilityCheck(vidId)
	if isAvalible is False:
		for (channelTitle, channelId, priority, pullError) in functions.getData('account', f'WHERE id=\"{childfrom}\"'):

			if avalibilityType == 'Deleted' or avalibilityType == 'Private':
				print(f"{functions.coloursB['red']}{avalibilityType.upper()}{functions.colours['reset']} - {vidId} | {channelTitle} | {title}")
			else:
				if avalibilityType == 'Unlisted' or avalibilityType == 'Striked':
					print(f"{functions.coloursB['yellow']}{avalibilityType.upper()}{functions.colours['reset']} - {vidId} | {channelTitle} | {title}")	

			if deleted == 0: # Video status just got deleted

				# Getting date
				formattedDate = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

				print(f'  ^ The first time detecting this as {avalibilityType}\n')
				functions.chData('content', vidId, 'deleted', 1)
				functions.chData('content', vidId, 'deletedtype', avalibilityType)
				functions.chData('content', vidId, 'deleteddate', formattedDate)
				if avalibilityType == 'Private':
					functions.msgAll(f"{title} from \'{channelTitle}\' just got Privated, not Deleted\n\n/send `{vidId}`", True)
				else:
					if avalibilityType == 'Deleted':
						functions.msgAll(f"{title} from \'{channelTitle}\' just got Deleted, not Privated\n\n/send `{vidId}`", True)
					else:
						if avalibilityType == 'Unlisted':
							functions.msgAll(f"{title} from \'{channelTitle}\' just got Unlisted\n\nhttps://www.youtube.com/watch?v={vidId}")
						else:
							if avalibilityType == 'Striked':
								functions.msgAll(f"{title} from \'{channelTitle}\' just got Striked by \'{striker}\'\n\n/send `{vidId}`", True)
	# If the content is avalible
	else:
		if deleted == 1: # Video status just got back online
			for (channelTitle, channelId, priority, pullError) in functions.getData('account', f'WHERE id=\"{childfrom}\"'):

				# Getting date
				formattedDate = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

				print(f"{functions.coloursB['green']}{avalibilityType.upper()}{functions.colours['reset']}  - {vidId} | {channelTitle} | {title}")
				print(f'  ^ The first time detecting this as {avalibilityType} (Again)\n')
				functions.chData('content', vidId, 'deleted', 0)
				functions.chData('content', vidId, 'deletedtype', 'Public')
				functions.chData('content', vidId, 'deleteddate', formattedDate)
				functions.msgAll(f"{title}. from \'{channelTitle}\' just got put back Online from {deletedtype}\nhttps://www.youtube.com/watch?v={vidId}", False)

threads = []
currentRequestNum = 0
for (title, vidId, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser) in functions.getData('content', 'ORDER BY deleted DESC'):

	currentRequestNum += 1

	count = len(f'{currentRequestNum}/{totalRows}') + len(f'{100/totalRows*currentRequestNum:.2f}%')
	terminalWidth = (originalTerminalWidth - count)

	print(f"{functions.coloursB['white']}{100/totalRows*currentRequestNum:.2f}%{functions.colours['reset']}\033[{terminalWidth}C{currentRequestNum}/{totalRows}", end = '\r')

	if runInBackround is True:
		t = threading.Thread(target=checkingAndInforming, args=(title, vidId, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser))
		threads.append(t)
		t.start()
		time.sleep(sleepTime)
	elif runInBackround is False:
		checkingAndInforming(title, vidId, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser)
	else:
		print("Please enter a 'runInBackround' value")
		break

if runInBackround:
	for t in threads:
		t.join()