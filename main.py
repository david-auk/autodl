import os
import yt_dlp
import scrapetube
import datetime
import functions

#functions.delData("content", "tYO5OWlihgo")
#quit()

requestuser = "scanner"

functions.getData("account", "id", 'ALL')
myCursorChannelRequest = functions.getDataCursor
for (channelTitle, id, priority) in myCursorChannelRequest:

	priorityColor = functions.colourPriority(priority)
	print(f"{priorityColor}•{functions.colours['reset']} {functions.coloursB['white']}{channelTitle}:{functions.colours['reset']}")

	videos = scrapetube.get_channel(id)	

	for video in videos:
		urlid = video['videoId']
		videoTitle = video['title']['runs'][0]['text']
		print(videoTitle + "\n")
		#functions.getData("content", "id", urlid, "contentCheck")
		entryExists = functions.getDataContentCheck(urlid)
		if entryExists:
			# Printing 'Succes' status for if the entry exists
			print(f"[{functions.coloursB['green']}√{functions.colours['reset']}] https://www.youtube.com/watch?v={urlid}\n")
			break #to next account
		else:
			# Printing 'Failed' status for if the entry exists
			print(f"[{functions.coloursB['red']}X{functions.colours['reset']}] https://www.youtube.com/watch?v={urlid}")
			
			# Getting date
			currentDate = datetime.datetime.now()
			formattedDate = currentDate.strftime("%d-%m-%Y")

			# Making the path filename friendly
			filename = functions.filenameFriendly(videoTitle)
			print(filename)
			quit()
			functions.addContentData(videoTitle,channelTitle,urlid,filename,"thumbnailPath",0,"N/A", requestuser,formattedDate)

			# Download file here

			# functions.chData("content", urlid, "downloaddate", "12-02-1992")

			print("\n")

print("end of myCursor loop")
functions.closeCursor()