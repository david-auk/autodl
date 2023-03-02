import os
import yt_dlp
import scrapetube
import datetime
import functions

## Basic definition start.

requestuser = "scanner" # This will be the value of the 'reqester' field in SQL
totalRecords = 0 # So we can count upwards	

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
		entryExists = functions.getDataContentCheck(vidId)
		if entryExists:

			# Printing 'Succes' status for if the entry exists
			print(f"[{functions.coloursB['green']}√{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}\n")
			break #to next account
			
		else:

			# Printing 'Failed' status for if the entry exists
			print(f"[{functions.coloursB['red']}X{functions.colours['reset']}] https://www.youtube.com/watch?v={vidId}")
			
			# Getting date
			currentDate = datetime.datetime.now()
			formattedDate = currentDate.strftime("%d-%m-%Y")

			# Making the path filename friendly
			filename = functions.filenameFriendly(videoTitle)
			functions.addContentData(videoTitle,channelTitle,vidId,filename,"N/A",0, requestuser,formattedDate)

			totalRecords += functions.addContentDataCursor.rowcount
			# Download file here

			# functions.chData("content", vidId, "downloaddate", "12-02-1992")

			print("\n")

if totalRecords:
	print(f"{functions.coloursB['white']}{totalRecords}{functions.colours['reset']} Records inserted.")
else:
	print("All up to date\n")
functions.closeCursor()