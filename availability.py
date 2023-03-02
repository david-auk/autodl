import functions

myCursorContentRequest = functions.getData('content', 'id', 'ALL')
for (title, childfrom, id, videopath, extention, deleted, requestuser, downloaddate) in myCursorContentRequest:
	isAvalible, avalibilityType = functions.avalibilityCheck(id)
	if isAvalible:
		print(f"[{functions.coloursB['green']}√{functions.colours['reset']}] {id} | {title}")
	else:
		print(f"[{functions.coloursB['red']}X{functions.colours['reset']}] {id} > {avalibilityType} | {title}")