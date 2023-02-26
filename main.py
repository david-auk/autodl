import os
import yt_dlp
import scrapetube
import datetime
import functions

functions.getData("account","id","ALL", "accountList")
myCursorChannelRequest = functions.getDataCursor
for (channelTitle, id, priority) in myCursorChannelRequest:

	priorityColor = functions.colourPriority(priority)
	print(f"{priorityColor}•{functions.colours['reset']} {channelTitle}:")

	videos = scrapetube.get_channel(id)	

	for video in videos:
		urlid = video['videoId']
		videoTitle = video['title']['runs'][0]['text']
		print(videoTitle + "\n")
		functions.getData("content", "id", urlid, "contentCheck")
		if functions.entryExists:
			print(f"[{functions.coloursB['green']}√{functions.colours['reset']}] https://www.youtube.com/watch?v={urlid}\n")

			break #to next account
		else:
			print(f"[{functions.coloursB['red']}X{functions.colours['reset']}] https://www.youtube.com/watch?v={urlid}")
			currentDate = datetime.datetime.now()
			formattedDate = currentDate.strftime("%d-%m-%Y")

			# functions.addContentData(videoTitle,channelTitle,urlid,"path","thumbnailPath",0,"N/A",formattedDate)

			# Download file here

			# functions.chData("content", urlid, "downloaddate", "12-02-1992")

			print("\n")

print("end of myCursor loop")
functions.closeCursor()