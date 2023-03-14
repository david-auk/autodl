import os
import argparse
import scrapetube
import datetime
import functions

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
	operator = '<'
	print(f"\n{functions.coloursB['white']}Type pull:{functions.colours['reset']} {functions.colourPriority(requiredPriority)}•{functions.colours['reset']}\n")
	requiredPriority += 1
else:
	requiredPriority = 'ALL'
	operator = '='

## Flags end.



for (channelTitle, id, priority) in functions.getData("account", "priority", operator, requiredPriority):

	# Creating the prompt with corosponding colour
	print(f"{functions.colourPriority(priority)}•{functions.colours['reset']} {functions.coloursB['white']}{channelTitle}:{functions.colours['reset']}")

	# Getting all the videos of current youtube channel in 'account' table
	videos = scrapetube.get_channel(id)	

	for video in videos:
		vidId = video['videoId']
		videoTitle = video['title']['runs'][0]['text']
		print(videoTitle)

		# Checking if the entry exists in database
		entryExists = False
		for x in functions.getData('content', 'id', '=', vidId):
			entryExists = True

		if entryExists:

			# Printing 'Succes' status for if the entry exists
			print(f"[{functions.coloursB['green']}√{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}\n")
			break #to next account
			
		else:

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
			success, vidInfo, uploadDate = functions.getFacts(vidId, channelTitle, filename)

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
					for x in functions.getData('content', 'id', '=', vidId):
						entryExists = True

					if entryExists is False:

						# Adding new entry to 'content' table
						rowsAdded = functions.addContentData(videoTitle,channelTitle,vidId,filename,videoExtention,0,'N/A','Public',requestuser,uploadDate)
						totalRecordsAdded += rowsAdded
			
				else:

					# Notify host downloading gives error
					functions.msgHost(f"Downloading https://www.youtube.com/watch?v={vidId} from {channelTitle}\ngave ERROR: {failureType}")

print(f"{functions.coloursB['white']}{totalRecordsAdded}{functions.colours['reset']} Records inserted.")
if totalRecordsSkipped:
	print(f"{functions.coloursB['yellow']}{totalRecordsSkipped}{functions.colours['reset']} Records Skipped.")