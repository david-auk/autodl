import logging
import functions
import secret
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
							  '/help - Show list of useful commands\n'
							  '/passwd - Check password\n'
							  '/latest - Ask for the latest data\n'
							  '/info - Get info about a link')

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

	if is_allowed_user(update, context):
		context.bot.send_message(chat_id=chat_id, text="Already authorized")
		return

	# Send a message to the user asking for their password
	context.bot.send_message(chat_id=chat_id, text="Please enter your password:")

	# Set the next handler to wait for the user's password
	context.user_data["next_handler"] = "check_password"


def ask_latest(update, context):
	"""Ask for the latest data using buttons."""

	# Check if the user is allowed to use the bot
	if is_allowed_user(update, context) is False:
		context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, you are not authorized to use this bot.")
		return

	if update.message.text[8:]:
		arg = update.message.text[8:]
		if arg.isdigit():
			if int(arg) < 69: # The max lines a messages can contain. Nice
				table = f'(SELECT * FROM content ORDER BY nr DESC LIMIT {arg})'
				statment = f'AS subquery ORDER BY nr ASC'
				totalRows = functions.countData(table, statment)
				maxLen = len(str(totalRows))
				latestContent = ''

				if totalRows:
					totalRows += 1
					for (title, id, childfrom, nr, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser) in functions.getData(table, statment):
						totalRows -= 1
						space = " " * (maxLen - len(str(totalRows)))
						latestContent += f"{totalRows}.{space} {childfrom} | {title}\n"
				else:
					latestContent='No Data.'

				context.bot.send_message(chat_id=update.message.chat.id, text=latestContent)
			else:
				context.bot.send_message(chat_id=update.message.chat.id, text='Requested over MAX lines')
		else:
			context.bot.send_message(chat_id=update.message.chat.id, text='Give a number as argument or use the buttons./latest')
		return

	keyboard = [[InlineKeyboardButton("10", callback_data='10'),InlineKeyboardButton("20", callback_data='20'),InlineKeyboardButton("30", callback_data='30')],[InlineKeyboardButton("Today", callback_data='today'),InlineKeyboardButton("Yesterday", callback_data='yesterday')]]

	reply_markup = InlineKeyboardMarkup(keyboard)

	update.message.reply_text('Please choose an option:', reply_markup=reply_markup)
	context.user_data["next_handler"] = "latest"


def buttonResolver(update, context):
	"""Handle the button press."""
	#chat_id = update.message.chat_id
	query = update.callback_query
	query.answer()
	buttonHandler = context.user_data["next_handler"]
	#context.user_data["next_handler"] = ''

	if buttonHandler == 'latest':
		if query.data == '10':
			text = 'Latest records:'
			table = f'(SELECT * FROM content ORDER BY nr DESC LIMIT 10)'
			statment = f'AS subquery ORDER BY nr ASC'
			# BC the final statment should look like 'SELECT * FROM (SELECT * FROM content ORDER BY nr DESC LIMIT {latestNum}) AS subquery ORDER BY nr ASC'
			# But the getData func requires a table
		else:
			if query.data == '20':
				text = 'Latest records:'
				table = f'(SELECT * FROM content ORDER BY nr DESC LIMIT 20)'
				statment = f'AS subquery ORDER BY nr ASC'
				# BC the final statment should look like 'SELECT * FROM (SELECT * FROM content ORDER BY nr DESC LIMIT {latestNum}) AS subquery ORDER BY nr ASC'
				# But the getData func requires a table
			else:
				if query.data == '30':
					text = 'Latest records:'
					table = f'(SELECT * FROM content ORDER BY nr DESC LIMIT 30)'
					statment = f'AS subquery ORDER BY nr ASC'
					# BC the final statment should look like 'SELECT * FROM (SELECT * FROM content ORDER BY nr DESC LIMIT {latestNum}) AS subquery ORDER BY nr ASC'
					# But the getData func requires a table
				else:
					if query.data == 'today':
						text = 'Today:'
						today = datetime.now().strftime('%d-%m-%Y')
						#table = 'content'
						#statment = f'WHERE uploaddate=\"{today}\"'
						table = f'(SELECT * FROM content WHERE downloaddate=\"{today}\")'
						statment = f'AS subquery ORDER BY nr ASC'
					else:
						if query.data == 'yesterday':
							text = 'Yesterday:'
							yesterday = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
							#table = 'content'
							#statment = f'WHERE uploaddate=\"{yesterday}\"'
							table = f'(SELECT * FROM content WHERE downloaddate=\"{yesterday}\")'
							statment = f'AS subquery ORDER BY nr ASC'

		#query.edit_message_text(text=f"{text}")

		totalRows = functions.countData(table, statment)
		maxLen = len(str(totalRows))
		latestContent = ''

		if totalRows:
			totalRows += 1
			for (title, id, childfrom, nr, videopath, extention, subtitles, uploaddate, downloaddate, deleteddate, deleted, deletedtype, requestuser) in functions.getData(table, statment):
				totalRows -= 1
				space = " " * (maxLen - len(str(totalRows)))
				latestContent += f"{totalRows}.{space} {childfrom} | {title}\n"
		else:
			latestContent='No Data.'

		#context.bot.send_message(chat_id=update.effective_chat.id, text=latestContent)
		query.edit_message_text(text=latestContent)

	# Incoming priority request
	elif buttonHandler == 'priority':
		channelChatInfo = context.user_data.get("channelChatInfo")
		channelChatInfo['priority'] = query.data
		query.delete_message()
		context.bot.edit_message_text(chat_id=channelChatInfo['chat_id'], message_id=channelChatInfo['message_id'], text=f"Prepairing backup: \'{channelChatInfo['ytLinkIdClean']}\' ⏳\n\nPriority: {channelChatInfo['priority']}\n\n(type name | type 'Cancel' to stop)\nChannel name:")
		
		context.user_data["next_handler"] = 'channel_name'
		context.user_data["channelChatInfo"] = channelChatInfo

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
	chat_id = update.message.chat_id

	# Check if the user's input is the correct password (if the previous handler was check_password)
	if context.user_data.get("next_handler") == "check_password":
		if message_text == password:
			context.bot.send_message(chat_id=chat_id, text="Your password is correct!")
			
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

			functions.msgHost(f"The user {name} just got added to the Database")

		else:
			context.bot.send_message(chat_id=chat_id, text="Sorry, that's not the correct password.")

	elif context.user_data.get("next_handler") == "channel_name":
		channelChatInfo = context.user_data.get("channelChatInfo")
		
		# Check if user wants to stop
		if message_text.lower() == 'cancel':
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
				functions.msgHost(f"User '{name}' just requested to backup channel: https://youtube.com/channel/{channelChatInfo['channel_id']} " + "{" + f" 'priority': '{channelChatInfo['priority']}', 'channel_name': '{channelChatInfo['channel_name']}' " + "}" + "\n\nAdd with messaging the link back")
				context.bot.edit_message_text(chat_id=channelChatInfo['chat_id'], message_id=channelChatInfo['message_id'], text=f"Added: {channelChatInfo['channel_name']} ⏳")
	
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

				succes, info, uploadDate = functions.getFacts(ytLinkId)
				if succes:
					videoTitle = info['title']
					videoExtention = info['ext']
					channelTitle = functions.accNameFriendly(info['uploader'])
					filename = functions.filenameFriendly(videoTitle)

					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️")
				else:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ❌\n\nCheck your link")	
					return				
			
				succes = functions.downloadThumbnail(ytLinkId, channelTitle, filename, info['thumbnail'])
				if succes:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️")	
				else:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ❌\n\nSomething weird is going on, Host contacted")
					return

				succes = functions.writeDescription(channelTitle, filename, info['description'])
				if succes:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️\n\nWriten description. ☑️\n\nDownloading video.")	
				else:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️\n\nWriten description. ❌\n\nPermission issue, Please contact host")
					return

				success, failureType = functions.downloadVid(ytLinkId, channelTitle, filename)
				if succes is False:
					context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Getting facts for: \'{ytLinkId}\'\n\nFacts retreved. ☑️\n\nDownloaded thumbnail. ☑️\n\nWriten description. ☑️\n\nDownloaded video. ❌ ERROR-type: {failureType}\nHost contacted.")
					return

				currentNum = functions.countData("content", 'ALL')

				downloaddate = datetime.now().strftime('%d-%m-%Y')

				functions.addContentData(videoTitle, ytLinkId, channelTitle, currentNum, filename, videoExtention, 0, uploadDate, downloaddate, 'N/A', 0, 'Public', chat_id)
				
				context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
				context.bot.send_message(chat_id=chat_id, text=f"Downloaded: \'{ytLinkId}\' ✅")
				
				if functions.subCheck(channelTitle, filename, videoExtention):
					functions.chData('content', ytLinkId, 'subtitles', 1)

				for (name, id, priority, authenticated) in functions.getData('chatid', f'WHERE id={chat_id}'):
					if priority != '1':
						functions.msgHost(f"{name}, Just downloaded: https://youtube.com/watch?v={ytLinkId}")
						functions.msgHost(f"/remove {ytLinkId}")
			else:
				if ytLinkType == 'channel':

					# Checking if the Id is already in the desired format
					if ytLinkId[:8] == 'channel/':
						message = False
						convertedChannelId = ytLinkId[8:]
					else:
						message = context.bot.send_message(chat_id=chat_id, text=f"Getting facts for: \'{ytLinkIdClean}\'")
						convertedChannelId = functions.getChannelId(ytLinkId)

					for (name, id, priority) in functions.getData('account', f'WHERE id=\"{convertedChannelId}\"'):
						if message:
							context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Already backing up channel: \'{name}\' ✅")
						else:
							context.bot.send_message(chat_id=chat_id, text=f"Already backing up channel: \'{name}\' ✅")
						return


					if message:
						context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"Prepairing backup: \'{ytLinkIdClean}\' ⏳")							
					else:
						message = context.bot.send_message(chat_id=chat_id, text=f"Prepairing backup: \'{ytLinkIdClean}\' ⏳")
			
					
					#context.bot.edit_message_text(chat_id=chat_id, text=f"Prepairing to backup: \'{ytLinkIdClean}\' ⏳", reply_markup=reply_markup)
					keyboard = [[InlineKeyboardButton("1 (fastest)", callback_data='1'),InlineKeyboardButton("2 (avg)", callback_data='2'),InlineKeyboardButton("3 (slowest)", callback_data='3')]]
					reply_markup = InlineKeyboardMarkup(keyboard)

					update.message.reply_text(f"assign a 'priority' value?", reply_markup=reply_markup)
					context.user_data["next_handler"] = "priority"
					context.user_data["channelChatInfo"] = {'message_id': f'{message.message_id}', 'chat_id': f'{chat_id}', 'channel_id': f'{convertedChannelId}', 'ytLinkIdClean': f'{ytLinkIdClean}'}
					return

		else:
			context.bot.send_message(chat_id=chat_id, text="Sorry, i don't understand..\nUse /help to see all compatible commands")

	context.user_data["next_handler"] = ""

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