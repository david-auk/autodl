import os
import argparse
import scrapetube
import datetime
import functions
import random

## Basic definition start.

requestuser = "scanner" # This will be the default value of the 'reqester' field in SQL
totalRecordsAdded = 0 # So we can count upwards	
totalRecordsSkipped = 0 # So we can count upwards
skipDownload = False

## Basic definition end.

## Flags start.

parser = argparse.ArgumentParser(description='A python script to check & download latestvideo')
parser.add_argument('-t', '--time', action='store_true', help='Enable verbose mode.')
args = parser.parse_args()
if args.time:
	now = datetime.datetime.now()
	if now.minute % 15 == 0:
		requiredPriority = 3 # One, two, three. All
	else:
		if now.minute % 10 == 0:
			requiredPriority = 2 # One, two
		else:
			requiredPriority = 1 # One
	print(f"\n{functions.coloursB['white']}Type pull:{functions.colours['reset']} {functions.colourPriority(requiredPriority)}•{functions.colours['reset']}\n")
	
	requiredPriority += 1 # Making the code above more human readable
	statement = f"WHERE priority < {requiredPriority} ORDER BY title ASC;"
else:
	statement = 'ORDER BY title ASC;'

## Flags end.


#functions

#quit()

for (channelTitle, id, priority, pullError) in functions.getData("account", statement):

	# Creating the prompt with corosponding colour
	print(f"{functions.colourPriority(priority)}•{functions.colours['reset']} {functions.coloursB['white']}{channelTitle}:{functions.colours['reset']}")

	# Getting all the videos of current youtube channel in 'account' table
	videos = scrapetube.get_channel(id)

	forLoopRan = False
	for video in videos:
		forLoopRan = True

		vidId = video['videoId']
		videoTitle = video['title']['runs'][0]['text']
		print(videoTitle)

		# Checking if the entry exists in database
		entryExists = False
		for x in functions.getData('content', f'WHERE id = \"{vidId}\" AND requestuser=\"{requestuser}\"'):
			entryExists = True

		if entryExists:

			# Printing 'Succes' status for if the entry exists
			print(f"[{functions.coloursB['green']}√{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}\n")
			break #to next account
			
		else:

			# Checking if video has been downloaded directly by user
			userRequested = False
			for (title, id, childfrom, nr, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, writtenrequestuser) in functions.getData('content', f'WHERE id=\"{vidId}\"'):
				print(f"[{functions.coloursB['cyan']}√{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}\n")
				userRequested = True

			if userRequested:
				continue # The previous video could hypothetically not be downloaded 

			# Checking if video is in premere
			isInPremiere = False
			if 'upcomingEventData' in video:
				isInPremiere = True

			# Skipping if video is in premiere
			if isInPremiere:
				print(f"[{functions.coloursB['yellow']}?{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}\n")
				totalRecordsSkipped += 1
				continue

			# Printing 'Failed' status for if the entry exists
			print(f"[{functions.coloursB['red']}X{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}\n")

			# Making the path filename friendly
			filename = functions.filenameFriendly(videoTitle)

			# Gather facts
			success, vidInfo, uploadDate = functions.getFacts(vidId)

			if success is False:
				print(f"[{functions.coloursB['yellow']}Skipping{functions.colours['reset']}]\n")
				functions.msgHost(f"Skipped https://www.youtube.com/watch?v={vidId}")
				totalRecordsSkipped += 1
				continue

			videoExtention = vidInfo['ext']

			# Deciding if the video will be downloaded
			if skipDownload is False:

				# Downloading the video's thumbnail
				functions.downloadThumbnail(vidId, channelTitle, filename, vidInfo['thumbnail'])
				print('') # Newline

				# Downloading the video's description
				functions.writeDescription(channelTitle, filename, vidInfo['description'])
				print('') # Newline

				# Downloading the actual video				
				success, failureType = functions.downloadVid(vidId, channelTitle, filename)
				print('') # Newline
				if success:

					# Checking if the video got added to the database while downloading
					entryExists = False
					for x in functions.getData('content', f'WHERE id=\"{vidId}\"'):
						entryExists = True

					if entryExists:
						print("Duplicate item, skipping")

					else:

						currentNum = functions.getMaxDataValue('content', 'nr') + 1

						# Getting the current date in desired format
						downloaddate = datetime.date.today().strftime('%d-%m-%Y')

						# Adding new entry to 'content' table
						totalRecordsAdded += functions.addContentData(videoTitle, vidId, channelTitle, currentNum, filename, videoExtention, 0, uploadDate, downloaddate, 'N/A', 0, 'Public', requestuser)
			
				else:

					# Notify host downloading gives error
					functions.msgHost(f"Downloading https://www.youtube.com/watch?v={vidId} from {channelTitle}\ngave ERROR: {failureType}")

				if functions.subCheck(channelTitle, filename, videoExtention):
					functions.chData('content', vidId, 'subtitles', 1)

	if forLoopRan is False:
		if pullError == 'N/A':
			currentChannelFacts = functions.getChannelFacts(id)
		else:
			if random.randint(1,6) == 1: # There is a one in six chance the loop will check new facts (it takes some time)
				print(f"{functions.coloursB['green']}Lucky{functions.colours['reset']} {functions.coloursB['white']}1/6{functions.colours['reset']}, refreshing channel")
				currentChannelFacts = functions.getChannelFacts(id)
			else:
				currentChannelFacts = pullError # Dont check if the account status is changed

		if currentChannelFacts != pullError: # First time detecting channel as 'empty'
			if currentChannelFacts == 'terminated':
				print(f"{functions.coloursB['red']}CHANNEL TERMINATED{functions.colours['reset']}\n[{functions.coloursB['red']}X{functions.colours['reset']}] https://youtube.com/channel/{id}\n")
				functions.msgHost(functions.escapeMarkdown(f"{channelTitle} gave a pull error: 'Terminated'\n\nhttps://youtube.com/channel/{id}"))
				functions.chData('account', id, 'pullerror', 'terminated')
			elif currentChannelFacts == 'no_uploads':
				print(f"{functions.coloursB['red']}NO VIDEOS FOUND{functions.colours['reset']}\n[{functions.coloursB['red']}X{functions.colours['reset']}] https://youtube.com/channel/{id}\n")
				functions.msgHost(f"{functions.escapeMarkdown(channelTitle)} gave a pull error: 'No Uploads'\n\nhttps://youtube.com/channel/{id}")
				functions.chData('account', id, 'pullerror', 'no_uploads')
		elif pullError == 'no_uploads': # There still is no new uploaded video
			print(f"{functions.coloursB['red']}NO VIDEOS FOUND{functions.colours['reset']}\n[{functions.coloursB['red']}X{functions.colours['reset']}] https://youtube.com/channel/{id}\n")
		elif pullError == 'terminated': # Channel is still terminated
			print(f"{functions.coloursB['red']}CHANNEL TERMINATED{functions.colours['reset']}\n[{functions.coloursB['red']}X{functions.colours['reset']}] https://youtube.com/channel/{id}\n")

print(f"{functions.coloursB['white']}{totalRecordsAdded}{functions.colours['reset']} Records inserted.")
if totalRecordsSkipped:
	print(f"{functions.coloursB['yellow']}{totalRecordsSkipped}{functions.colours['reset']} Records Skipped.")