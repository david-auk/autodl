import os
import scrapetube
import datetime
import functions

from yt_dlp import YoutubeDL

## Basic definition start.

requestuser = "scanner" # This will be the default value of the 'reqester' field in SQL
totalRecordsAdded = 0 # So we can count upwards	
totalRecordsSkipped = 0 # So we can count upwards
skipDownload = False

## Basic definition end.

myCursorChannelRequest = functions.getData("account", "id", 'ALL')
for (channelTitle, id, priority) in myCursorChannelRequest:

	# Creating the prompt with corosponding colour
	priorityColor = functions.colourPriority(priority)
	print(f"{priorityColor}•{functions.colours['reset']} {functions.coloursB['white']}{channelTitle}:{functions.colours['reset']}")

	# Getting all the videos of current youtube channel in 'account' table
	videos = scrapetube.get_channel(id)	

	for video in videos:
		vidId = video['videoId']
		videoTitle = video['title']['runs'][0]['text']
		print(videoTitle)
		entryExists = functions.getDataContentCheck('content', vidId)
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
				print(f"[{functions.coloursB['yellow']}?{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}\nVideo in premiere, skipping\n")
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
				totalRecordsSkipped += 1
				continue

			videoExtention = vidInfo['ext']

			# Deciding if the video will be downloaded
			if skipDownload is False:

				# Downloading the video's thumbnail
				functions.downloadThumbnail(vidId, channelTitle, filename, vidInfo['thumbnail'])
				print('') # Newline

				# Downloading the video's thumbnail
				functions.writeDescription(channelTitle, filename, vidInfo['description'])
				print('') # Newline

				# Downloading the actual video				
				success, failureType = functions.downloadVid(vidId, channelTitle, filename)
				print('') # Newline
				if success:

					# Adding new entry to 'content' table
					functions.addContentData(videoTitle,channelTitle,vidId,filename,videoExtention,0,'N/A','public',requestuser,uploadDate)
					totalRecordsAdded += functions.addContentDataCursor.rowcount
			
				else:

					# Notify host downloading gives error
					functions.msgHost(f"Downloading https://www.youtube.com/watch?v={vidId} from {channelTitle}\ngave ERROR: {failureType}")

			## Adding new entry to 'content' table
			#functions.addContentData(videoTitle,channelTitle,vidId,filename,videoExtention,0,'N/A','public',requestuser,uploadDate)
			#totalRecordsAdded += functions.addContentDataCursor.rowcount

print(f"{functions.coloursB['white']}{totalRecordsAdded}{functions.colours['reset']} Records inserted.")
if totalRecordsSkipped:
	print(f"{functions.coloursB['yellow']}{totalRecordsSkipped}{functions.colours['reset']} Records Skipped.")