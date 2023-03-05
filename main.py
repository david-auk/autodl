import os
import scrapetube
import datetime
import functions

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
		print(videoTitle + "\n")
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
			print(f"[{functions.coloursB['red']}X{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}")
			
			# Getting date
			currentDate = datetime.datetime.now()
			formattedDate = currentDate.strftime("%d-%m-%Y")

			# Making the path filename friendly
			filename = functions.filenameFriendly(videoTitle)

			# Deciding if the video will be downloaded
			if skipDownload:
				functions.addContentData(videoTitle,channelTitle,vidId,filename,'N/A',0,'N/A','public',requestuser,formattedDate)
				totalRecordsAdded += functions.addContentDataCursor.rowcount
			else:

				# Downloading the acctual video
				success, failureType = functions.downloadVid(vidId, channelTitle, filename)
				if success:

					# Adding the record to the 'Content' table
					functions.addContentData(videoTitle,channelTitle,vidId,filename,'N/A',0,'N/A','public',requestuser,formattedDate)
					totalRecordsAdded += functions.addContentDataCursor.rowcount
				else:

					# Notify host downloading gives error
					functions.msgHost(f"Downloading https://www.youtube.com/watch?v={vidId} from {channelTitle}\ngave ERROR: {failureType}")

print(f"{functions.coloursB['white']}{totalRecordsAdded}{functions.colours['reset']} Records inserted.")
if totalRecordsSkipped:
	print(f"{functions.coloursB['yellow']}{totalRecordsSkipped}{functions.colours['reset']} Records Skipped.")