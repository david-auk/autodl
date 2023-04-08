import logging
import functions
import secret
import time
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

# Define password variable
password = secret.telegram['credentials']['userpass']

# Define handlers for each command
def start(update, context):
	"""Send a message when the command /start is issued."""
	update.message.reply_text('Welcome to the *Telegram Command Interface*\n\nUse: /help', parse_mode='MarkdownV2')
	user = update.message.from_user
	chat_id = update.message.from_user.id
	name = f"@{user.username}"
	if name == '@':
		name = user.first_name

	userExists = False
	for x in functions.getData('chatid', f'WHERE id=\"{chat_id}\"'):
		userExists = True

	if userExists:
		functions.chData('chatid', chat_id, 'name', name)
	else:
		functions.addChatIdData(name, chat_id, 'N/A', 'N/A')

def helpMenu(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('The following commands are available:\n\n'
							  'Aurhorise using: /passwd\n\n'
							  'Send me a link!\n'
							  'I\'ll download the link or add a channel to backup\n\n'
							  'View the latest videos with: /latest \n'
							  '/info - Get info about a link\n'
							  '/send VIDID to view the content')

def is_allowed_user(update, context):
	"""Check if the current user ID is allowed."""
	# Get the user ID
	chat_id = update.message.from_user.id

	# Check if the user ID is in the AllowedUserID variable
	userIsAllowed = False
	for (name, id, priority, authenticated) in functions.getData('chatid', f'WHERE id=\"{chat_id}\"'):
		if authenticated == '1':
			userIsAllowed = True

	if userIsAllowed:
		return True
	else:
		return False

def check_password(update, context):
	"""Check the user's password."""
	# Get the chat ID
	chat_id = update.message.chat_id
	userMessageId = update.message.message_id

	if is_allowed_user(update, context):
		message = context.bot.send_message(chat_id=chat_id, text="Already authorized ✅")
		time.sleep(1.5)
		context.bot.delete_message(chat_id=chat_id, message_id=userMessageId)
		context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
		return

	# Send a message to the user asking for their password
	message = context.bot.send_message(chat_id=chat_id, text="Please enter your password:")

	# Set the next handler to wait for the user's password
	context.user_data["passwdinfo"] = {'user_message_id': f'{userMessageId}', 'bot_message_id': f'{message.message_id}'}
	context.user_data["next_handler"] = "check_password"


def ask_latest(update, context):
	"""Ask for the latest data using buttons."""

	chat_id = update.message.chat_id
	userMessageId = update.message.message_id
	# Check if the user is allowed to use the bot
	if is_allowed_user(update, context) is False:
		context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, you are not authorized to use this bot.")
		return

	if update.message.text[8:]:
		arg = update.message.text[8:]
		if arg.isdigit():
			if int(arg) < 69: # The max lines a messages can contain. Nice
				table = f'(SELECT * FROM content ORDER BY downloaddate DESC LIMIT {arg})'
				statment = f'AS subquery ORDER BY downloaddate ASC'
				totalRows = functions.countData(table, statment)
				maxLen = len(str(totalRows))
				latestContent = ''

				if totalRows:
					totalRows += 1
					for (title, id, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser) in functions.getData(table, statment):
						formattedDate = functions.getDate(str(downloaddate))
						totalRows -= 1
						space = " " * (maxLen - len(str(totalRows)))
						latestContent += f"{totalRows}.{space} {childfrom} | {title} ({formattedDate[1]}/{formattedDate[0]}, {formattedDate[3]}:{formattedDate[4]})\n"
				else:
					latestContent='No Data.'

				keyboard = [[InlineKeyboardButton("🗑️", callback_data='delete')]]
				reply_markup = InlineKeyboardMarkup(keyboard)

				#context.bot.edit_message_text(text=latestContent, chat_id=latestRequestInfo['chat_id'], message_id=latestRequestInfo['message_id'], reply_markup=reply_markup)
				message = context.bot.send_message(chat_id=update.message.chat.id, text=latestContent, reply_markup=reply_markup)
				
				context.user_data["next_handler"] = "delete"
				context.user_data["deleteMessage"] = {'message_id': f'{message.message_id}', 'chat_id': f'{update.message.chat.id}', 'userMessage_id': f'{userMessageId}'}
			else:
				context.bot.send_message(chat_id=update.message.chat.id, text='Requested over MAX lines')
		else:
			context.bot.send_message(chat_id=update.message.chat.id, text='Give a number as argument or use the buttons./latest')

		return

	downloadedToday = False
	#for x in functions.getData('content', f'WHERE downloaddate=\"{datetime.now().strftime("%d-%m-%Y")}\"'):
	for x in functions.getData('content', f'WHERE LEFT(downloaddate, 8)=\"{datetime.now().strftime("%Y%m%d")}\"'):
		downloadedToday = True

	downloadedYesterday = False
	#for x in functions.getData('content', f'WHERE downloaddate=\"{(datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")}\"'):
	for x in functions.getData('content', f'WHERE LEFT(downloaddate, 8)=\"{(datetime.now() - timedelta(days=1)).strftime("%Y%m%d")}\"'):
		downloadedYesterday = True

	if downloadedToday and downloadedYesterday:
		keyboard = [[InlineKeyboardButton("10", callback_data='10'),InlineKeyboardButton("20", callback_data='20'),InlineKeyboardButton("30", callback_data='30'),InlineKeyboardButton("Cancel", callback_data='cancel')],[InlineKeyboardButton("Today", callback_data='today'),InlineKeyboardButton("Yesterday", callback_data='yesterday')]]
	elif downloadedToday:
		keyboard = [[InlineKeyboardButton("10", callback_data='10'),InlineKeyboardButton("20", callback_data='20'),InlineKeyboardButton("30", callback_data='30'),InlineKeyboardButton("Cancel", callback_data='cancel')],[InlineKeyboardButton("Today", callback_data='today')]]
	elif downloadedYesterday:
		keyboard = [[InlineKeyboardButton("10", callback_data='10'),InlineKeyboardButton("20", callback_data='20'),InlineKeyboardButton("30", callback_data='30'),InlineKeyboardButton("Cancel", callback_data='cancel')],[InlineKeyboardButton("Yesterday", callback_data='yesterday')]]
	else:
		keyboard = [[InlineKeyboardButton("10", callback_data='10'),InlineKeyboardButton("20", callback_data='20'),InlineKeyboardButton("30", callback_data='30'),InlineKeyboardButton("Cancel", callback_data='cancel')]]

	reply_markup = InlineKeyboardMarkup(keyboard)

	message = context.bot.send_message(chat_id=chat_id, text=f'Please choose an option:', reply_markup=reply_markup)
	context.user_data["latestRequestInfo"] = {'message_id': f'{message.message_id}', 'chat_id': f'{chat_id}', 'userMessage_id': f'{userMessageId}'}
	context.user_data["next_handler"] = "latest"

def buttonResolver(update, context):
	"""Handle the button press."""
	#chat_id = update.message.chat_id
	query = update.callback_query
	query.answer()
	buttonHandler = context.user_data["next_handler"]
	#context.user_data["next_handler"] = ''

	if buttonHandler == 'latest':
		latestRequestInfo = context.user_data.get("latestRequestInfo")
		if query.data == 'cancel':
			context.bot.edit_message_text(chat_id=latestRequestInfo['chat_id'], message_id=latestRequestInfo['message_id'], text="Canceled request.")
			time.sleep(1.5)
			context.bot.delete_message(chat_id=latestRequestInfo['chat_id'], message_id=latestRequestInfo['userMessage_id'])
			context.bot.delete_message(chat_id=latestRequestInfo['chat_id'], message_id=latestRequestInfo['message_id'])
			return
		else:
			if query.data == '10':
				dateSpecified = False
				table = f'(SELECT * FROM content ORDER BY downloaddate DESC LIMIT 10)'
				statment = f'AS subquery ORDER BY downloaddate ASC'
				# BC the final statment should look like 'SELECT * FROM (SELECT * FROM content ORDER BY nr DESC LIMIT {latestNum}) AS subquery ORDER BY nr ASC'
				# But the getData func requires a table
			else:
				if query.data == '20':
					dateSpecified = False
					table = f'(SELECT * FROM content ORDER BY downloaddate DESC LIMIT 20)'
					statment = f'AS subquery ORDER BY downloaddate ASC'
					# BC the final statment should look like 'SELECT * FROM (SELECT * FROM content ORDER BY nr DESC LIMIT {latestNum}) AS subquery ORDER BY nr ASC'
					# But the getData func requires a table
				else:
					if query.data == '30':
						dateSpecified = False
						table = f'(SELECT * FROM content ORDER BY downloaddate DESC LIMIT 30)'
						statment = f'AS subquery ORDER BY downloaddate ASC'
						# BC the final statment should look like 'SELECT * FROM (SELECT * FROM content ORDER BY nr DESC LIMIT {latestNum}) AS subquery ORDER BY nr ASC'
						# But the getData func requires a table
					else:
						if query.data == 'today':
							dateSpecified = True
							today = datetime.now().strftime('%Y%m%d')
							#table = 'content'
							#statment = f'WHERE uploaddate=\"{today}\"'
							table = f'(SELECT * FROM content WHERE LEFT(downloaddate, 8)=\"{today}\")'
							statment = f'AS subquery ORDER BY downloaddate ASC'
						else:
							if query.data == 'yesterday':
								dateSpecified = True
								yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
								#table = 'content'
								#statment = f'WHERE uploaddate=\"{yesterday}\"'
								table = f'(SELECT * FROM content WHERE LEFT(downloaddate, 8)=\"{yesterday}\")'
								statment = f'AS subquery ORDER BY downloaddate ASC'

		#query.edit_message_text(text=f"{text}")

		totalRows = functions.countData(table, statment)
		maxLen = len(str(totalRows))
		latestContent = ''

		if totalRows:
			totalRows += 1
			for (title, id, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser) in functions.getData(table, statment):
				totalRows -= 1
				space = " " * (maxLen - len(str(totalRows)))
				formattedDate = functions.getDate(str(downloaddate))
				if dateSpecified:
					latestContent += f"{totalRows}.{space} {childfrom} | {title} ({formattedDate[3]}:{formattedDate[4]})\n"
				elif dateSpecified is False:
					latestContent += f"{totalRows}.{space} {childfrom} | {title} ({formattedDate[1]}/{formattedDate[0]}, {formattedDate[3]}:{formattedDate[4]})\n"
		else:
			latestContent='No Data.'

		keyboard = [[InlineKeyboardButton("🗑️", callback_data='delete')]]
		reply_markup = InlineKeyboardMarkup(keyboard)

		context.bot.edit_message_text(text=latestContent, chat_id=latestRequestInfo['chat_id'], message_id=latestRequestInfo['message_id'], reply_markup=reply_markup)

		context.user_data["next_handler"] = "delete"
		context.user_data["deleteMessage"] = {'message_id': f"{latestRequestInfo['message_id']}", 'chat_id': f"{latestRequestInfo['chat_id']}", 'userMessage_id': f"{latestRequestInfo['userMessage_id']}"}
					
	elif buttonHandler == 'delete':
		deleteMessage = context.user_data.get("deleteMessage")
		context.bot.delete_message(chat_id=deleteMessage['chat_id'], message_id=deleteMessage['userMessage_id'])
		context.bot.delete_message(chat_id=deleteMessage['chat_id'], message_id=deleteMessage['message_id'])

	# Incoming priority request
	elif buttonHandler == 'priority': 
		channelChatInfo = context.user_data.get("channelChatInfo")
		channelChatInfo['priority'] = query.data
		if channelChatInfo['priority'] == 'cancel':
			#query.delete_message()
			context.bot.edit_message_text(chat_id=channelChatInfo['chat_id'], message_id=channelChatInfo['message_id'], text="Canceled request.")
			context.user_data["next_handler"] = ""
			context.user_data["channelChatInfo"] = ""
			return

		#query.delete_message()
		context.bot.edit_message_text(chat_id=channelChatInfo['chat_id'], message_id=channelChatInfo['message_id'], text=f"Prepairing backup: \'{channelChatInfo['ytLinkIdClean']}\' ⏳\n\nPriority: {channelChatInfo['priority']}\n\nChannel name:\n[ Type ChannelName | 'Cancel' to stop ]")
		
		context.user_data["next_handler"] = 'channel_name'
		context.user_data["channelChatInfo"] = channelChatInfo

def sendContent(update, context):
	chat_id = update.message.chat_id

	# Check if the user is allowed to use the bot
	if is_allowed_user(update, context) is False:
		context.bot.send_message(chat_id=chat_id, text="Sorry, you are not authorized to use this bot.")
		return

	initialUserMessageId = update.message.message_id
	message_text = update.message.text
	link = message_text[6:]

	if link:
		isYtLink, ytLinkType, ytLinkId, ytLinkIdClean = functions.isYtLink(link)

		if ytLinkType == 'video':
			vidId = ytLinkId
		else:
			vidId = link

		entryExists = False
		for x in functions.getData('content', f'WHERE id=\"{vidId}\"'):
			entryExists = True

		if entryExists:
			for (name, id, priority, authenticated) in functions.getData('chatid', f'WHERE id=\"{chat_id}\"'):
				if priority != '1':
					functions.msgHost(f"Server is sending User, {name}: `{ytLinkId}`", True)
				
				sendActualContent(update, context, vidId)
				return

		else:
			message = context.bot.send_message(chat_id=chat_id, text="Video not found. ❌")
			responseMessageId = message.message_id
			time.sleep(3)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=responseMessageId)

	else:
		message = context.bot.send_message(chat_id=chat_id, text="Send a link in the format: /send VIDID | /send youtu.be/VIDID")
		responseMessageId = message.message_id
		time.sleep(5)
		context.bot.delete_message(chat_id=chat_id, message_id=responseMessageId)
		context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
		return

def sendActualContent(update, context, vidId):
	chat_id = update.message.chat_id

	# Getting facts
	rootDownloadDir = secret.configuration['general']['backupDir']
	for (title, id, childfrom, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, writtenrequestuser) in functions.getData('content', f'WHERE id=\"{vidId}\"'):
		accountPath = f'{rootDownloadDir}/{childfrom}'
		pathDictionary = {
			'audio': f'{rootDownloadDir}/{childfrom}/{videopath}.mp3',
			'video': f'{rootDownloadDir}/{childfrom}/{videopath}.{extention}',
			'thumbnail': f'{rootDownloadDir}/{childfrom}/thumbnail/{videopath}.jpg',
			'description': f'{rootDownloadDir}/{childfrom}/description/{videopath}.txt'
		}

	humanReadableSize = functions.humanReadableSize(pathDictionary['video'])

	# Send the video file to the user
	statusMessage = context.bot.send_message(chat_id=chat_id, text=f"Uploading video ({humanReadableSize}) to file.io 1/4\nThis could take a while.")
	animationMessage = context.bot.send_message(chat_id=chat_id, text="⏳")

	with open(pathDictionary['description'], 'r') as file:
		description = file.read()

	link = functions.uploadFile(title, description, pathDictionary['video'])

	# Video
	context.bot.send_message(chat_id=chat_id, text=link)
	context.bot.delete_message(chat_id=chat_id, message_id=animationMessage.message_id)
	context.bot.delete_message(chat_id=chat_id, message_id=statusMessage.message_id)

	# Audio
	statusMessage = context.bot.send_message(chat_id=chat_id, text="Generating Audio from Video 2/4")
	animationMessage = context.bot.send_message(chat_id=chat_id, text="⏳")
	functions.subprocess.call(['ffmpeg', '-y', '-i', pathDictionary['video'], '-vn', '-acodec', 'libmp3lame', '-qscale:a', '2', '-metadata', f'artist={childfrom}', '-metadata', f'title={title}','-loglevel', 'quiet', pathDictionary['audio']])
	context.bot.send_audio(chat_id=chat_id, audio=open(pathDictionary['audio'], 'rb'), caption='')
	context.bot.delete_message(chat_id=chat_id, message_id=animationMessage.message_id)
	functions.os.remove(pathDictionary['audio'])

	# Thumbnail
	context.bot.edit_message_text(chat_id=chat_id, message_id=statusMessage.message_id, text="Sending Thumbnail 3/4")
	context.bot.send_document(chat_id=chat_id, document=open(pathDictionary['thumbnail'], 'rb'), caption='')

	# Description
	context.bot.edit_message_text(chat_id=chat_id, message_id=statusMessage.message_id, text="Sending Description 4/4")
	context.bot.send_document(chat_id=chat_id, document=open(pathDictionary['description'], 'rb'), caption='')

	# Cleanup
	context.bot.delete_message(chat_id=chat_id, message_id=statusMessage.message_id)


def get_info(update, context):
	"""Listen for user input and do an if statement."""

	# Check if the user is allowed to use the bot
	if is_allowed_user(update, context) is False:
		context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, you are not authorized to use this bot.")
		return

	update.message.reply_text('Please enter a link:')
	link = update.message.text

	# Perform the if statement based on the link
	if 'example.com' in link:
		update.message.reply_text('This is an example link.')
	else:
		update.message.reply_text('Sorry, I do not recognize this link.')


def link(update, context):
	"""Handle links sent by the user."""
	# Get the message text and chat ID
	message_text = update.message.text
	userMessageId = update.message.message_id
	chat_id = update.message.chat_id

	# Check if the user's input is the correct password (if the previous handler was check_password)
	if context.user_data.get("next_handler") == "check_password":
		passwdInfo = context.user_data.get("passwdinfo")
		initialUserMessageId = passwdInfo['user_message_id']
		initialBotRespondMessageId = passwdInfo['bot_message_id']
		passwordMessageId = userMessageId
		if message_text == password:
			message = context.bot.send_message(chat_id=chat_id, text="Correct password ✅")
			finalBotResponceMessageId = message.message_id

			user = update.message.from_user
			name = f"@{user.username}"
			if name == '@':
				name = user.first_name

			userExists = False
			hasPriorityValue = False
			for (name, id, priority, authenticated) in functions.getData('chatid', f'WHERE id=\"{chat_id}\"'):
				userExists = True
				if priority == 'N/A':
					hasPriorityValue = True

			if userExists:
				functions.chData('chatid', chat_id, 'authenticated', '1')
				if hasPriorityValue:
					functions.chData('chatid', chat_id, 'priority', '3')
			else:
				functions.addChatIdData(name, chat_id, '3', '1')
			if priority != '1':
				functions.msgHost(f"The user {name} just got added to the Database", False)

			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=initialBotRespondMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=passwordMessageId)
			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=finalBotResponceMessageId)
		else:
			message = context.bot.send_message(chat_id=chat_id, text="Sorry, that's not the correct password.")
			finalBotResponceMessageId = message.message_id
			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=initialBotRespondMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=passwordMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=finalBotResponceMessageId)

		context.user_data["next_handler"] = ""
		return

	elif context.user_data.get("next_handler") == "channel_name":
		channelChatInfo = context.user_data.get("channelChatInfo")
		
		# Check if user wants to stop
		if message_text.lower().replace(" ", "") == 'cancel':
			context.bot.edit_message_text(chat_id=chat_id, message_id=channelChatInfo['message_id'], text="Canceled request.")		
			context.user_data["next_handler"] = ""
			context.user_data["channelChatInfo"] = ""
			return

		channelChatInfo['channel_name'] = functions.accNameFriendly(message_text)

		context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
		print(channelChatInfo)
		for (name, id, priority, authenticated) in functions.getData('chatid', f'WHERE id={chat_id}'):
			if priority == '1':
				functions.addAccountData(channelChatInfo['channel_name'], channelChatInfo['channel_id'], channelChatInfo['priority'])
				context.bot.edit_message_text(chat_id=channelChatInfo['chat_id'], message_id=channelChatInfo['message_id'], text=f"Added: {channelChatInfo['channel_name']} ✅")
			else:
				functions.msgHost(f"User '{name}'\njust requested to backup channel: " + "{" + f" 'priority': '{channelChatInfo['priority']}', 'name': '{channelChatInfo['channel_name']}' " + "}" + "\n\nAdd with messaging the link back", False)
				functions.msgHost(f"https://youtube.com/channel/{channelChatInfo['channel_id']}", False)
				context.bot.edit_message_text(chat_id=channelChatInfo['chat_id'], message_id=channelChatInfo['message_id'], text=f"Requested: {channelChatInfo['channel_name']} ⏳")
			
			context.user_data["next_handler"] = ""
			return
	# Handle other messages as usual
	else:
		
		# Check if the user is allowed to use the bot
		if is_allowed_user(update, context) is False:
			context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, you are not authorized to use this bot.")
			return

		# Check if the message is a link
		if message_text[:7] == 'http://' or message_text[:8] == 'https://':
			isYtLink, ytLinkType, ytLinkId, ytLinkIdClean = functions.isYtLink(message_text)

			# If link is not a usable link the function is exited
			if isYtLink is False:
				context.bot.send_message(chat_id=chat_id, text=f"Link not recognized..\nUse /help to see all compatible commands")
				return

			if ytLinkType == 'video':

				# Checking if the video got added to the database while downloading
				entryExists = False
				for x in functions.getData('content', f'WHERE id=\"{ytLinkId}\"'):
					entryExists = True

				if entryExists:
					context.bot.send_message(chat_id=chat_id, text=f"Already downloaded video: \'{ytLinkId}\' ✅")
					return

				message = context.bot.send_message(chat_id=chat_id, text=f"Getting facts for: \'{ytLinkId}\'")
				message_id = update.message.message_id

				succes, info = functions.getFacts(ytLinkId)
				
				if succes:
					videoTitle = info['title']
					videoExtention = info['ext']
					if 'release_date' in info:
						uploadDate = info['release_date']
					else:
						uploadDate = info['upload_date']

					channelId = functions.cleanChannelLink(info['channel_url'])

					# Check if the channel is getting backed up (and if there is a custom name)
					foundChannel = False
					for x in functions.getData('account', f'WHERE id=\"{channelId}\"'):
						foundChannel = True
						channelTitle = x[0]
					if foundChannel is False:
						channelTitle = functions.accNameFriendly(info['uploader'])

					filename = functions.filenameFriendly(videoTitle)

					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️")
				else:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ❌\n\nCheck your link")	
					return				

				# Downloading thumbnail
				succes = functions.downloadThumbnail(ytLinkId, channelTitle, filename, info['thumbnail'])
				if succes:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️")	
				else:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ❌\n\nSomething weird is going on, Host contacted")
					return

				# Downloading description
				succes = functions.writeDescription(channelTitle, filename, info['description'])
				if succes:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️\n\nWriten description. ☑️\n\nDownloading video.")	
				else:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️\n\nWriten description. ❌\n\nPermission issue, Please contact host")
					return

				# Downloading video
				success, failureType = functions.downloadVid(ytLinkId, channelTitle, filename)
				if succes is False:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️\n\nWriten description. ☑️\n\nDownloaded video. ❌ ERROR-type: {failureType}\nHost contacted.")
					return

				downloaddate = datetime.now().strftime('%Y%m%d%H%M%S')

				functions.addContentData(videoTitle, ytLinkId, channelTitle, filename, videoExtention, 0, uploadDate, downloaddate, 0, 0, 'Public', chat_id)
				
				context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
				context.bot.send_message(chat_id=chat_id, text=f"Downloaded: \'{ytLinkId}\' ✅")
				
				if functions.subCheck(channelTitle, filename, videoExtention):
					functions.chData('content', ytLinkId, 'subtitles', 1)

				for (name, id, priority, authenticated) in functions.getData('chatid', f'WHERE id={chat_id}'):
					if priority != '1':
						functions.msgHost(f"{name}, Just downloaded: https://youtube.com/watch?v={ytLinkId}", False)
						functions.msgHost(f"/remove `{ytLinkId}`", True)
			else:
				if ytLinkType == 'channel':

					# Checking if the Id is already in the desired format
					if ytLinkId[:8] == 'channel/':
						message = False
						convertedChannelId = ytLinkId[8:]
					else:
						message = context.bot.send_message(chat_id=chat_id, text=f"Getting facts for: \'{ytLinkIdClean}\'")
						succes, convertedChannelId = functions.getChannelId(ytLinkId)
						if succes is False:
							context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"ERROR 404, Cant find channel: \'{ytLinkIdClean}\' ❌")
							return

					for (name, id, priority, pullError) in functions.getData('account', f'WHERE id=\"{convertedChannelId}\"'):
						if message:
							context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Already backing up channel: \'{name}\' ✅")
						else:
							context.bot.send_message(chat_id=chat_id, text=f"Already backing up channel: \'{name}\' ✅")
						return

					keyboard = [[InlineKeyboardButton("1 (fast)", callback_data='1'),InlineKeyboardButton("2 (avg)", callback_data='2'),InlineKeyboardButton("3 (slow)", callback_data='3'),InlineKeyboardButton("Cancel", callback_data='cancel')]]
					reply_markup = InlineKeyboardMarkup(keyboard)

					if message:
						context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Prepairing backup: \'{ytLinkIdClean}\' ⏳\n\nPriority:", reply_markup=reply_markup)							
					else:
						message = context.bot.send_message(chat_id=chat_id, text=f"Prepairing backup: \'{ytLinkIdClean}\' ⏳\n\nPriority:", reply_markup=reply_markup)
	
					context.user_data["next_handler"] = "priority"
					context.user_data["channelChatInfo"] = {'message_id': f'{message.message_id}', 'chat_id': f'{chat_id}', 'channel_id': f'{convertedChannelId}', 'ytLinkIdClean': f'{ytLinkIdClean}'}
					return

		else:
			context.bot.send_message(chat_id=chat_id, text="Sorry, i don't understand..\nUse /help to see all compatible commands")

	context.user_data["next_handler"] = ""

def delete(update, context):
	chat_id = update.message.chat_id

	# Check if the user is allowed to use the bot
	if is_allowed_user(update, context) is False:
		context.bot.send_message(chat_id=chat_id, text="Sorry, you are not authorized to use this bot.")
		return

	initialUserMessageId = update.message.message_id
	message_text = update.message.text
	link = message_text[8:]
	
	if not link:
		message = context.bot.send_message(chat_id=chat_id, text="Send a link in the format: /delete youtu.be/VIDID")
		responseMessageId = message.message_id
		time.sleep(3)
		context.bot.delete_message(chat_id=chat_id, message_id=responseMessageId)
		context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
		return

	isYtLink, ytLinkType, ytLinkId, ytLinkIdClean = functions.isYtLink(link)
	if isYtLink is False:
		message = context.bot.send_message(chat_id=chat_id, text="Send a youtube: Channel, Video ❌")
		responseMessageId = message.message_id
		time.sleep(3)
		context.bot.delete_message(chat_id=chat_id, message_id=responseMessageId)
		context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
		return

	if ytLinkType == 'video':
		entryExists = False
		for x in functions.getData('content', f'WHERE id=\"{ytLinkId}\"'):
			entryExists = True

		if entryExists:
			for (name, id, priority, authenticated) in functions.getData('chatid', f'WHERE id=\"{chat_id}\"'):
				if priority == '1':
					message = context.bot.send_message(chat_id=chat_id, text="Deleting video ⏳")
					functions.delVid(ytLinkId)
					time.sleep(0.5)
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text="Video deleted from backup. ✅")
				else:
					context.bot.send_message(chat_id=chat_id, text="Sent removal request to host ⏳")
					functions.msgHost(f"User, {name} just requested to remove https://youtu.be/{ytLinkId}")
		else:
			message = context.bot.send_message(chat_id=chat_id, text="Video was not downloaded. ✅")
			responseMessageId = message.message_id
			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=responseMessageId)

	elif ytLinkType == 'channel':
		entryExists = False
		for x in functions.getData('account', f'WHERE id=\"{ytLinkId}\"'):
			entryExists = True



def error(update, context):
	"""Echo the user message."""
	update.message.reply_text(f"Unknown command: {update.message.text}")


def main():
	# Set up the Telegram bot
	updater = Updater(secret.telegram['credentials']['token'], use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add handlers for different commands
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", helpMenu))
	dp.add_handler(CommandHandler("passwd", check_password))
	dp.add_handler(CommandHandler("latest", ask_latest))
	dp.add_handler(CommandHandler("delete", delete))
	dp.add_handler(CommandHandler("send", sendContent))
	dp.add_handler(CallbackQueryHandler(buttonResolver))
	dp.add_handler(CommandHandler("info", get_info))
	dp.add_handler(MessageHandler(Filters.text & (~Filters.command), link))
	dp.add_handler(MessageHandler(Filters.text & Filters.command, error))

	# Start the bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process is stopped
	updater.idle()

if __name__ == '__main__':
	main()