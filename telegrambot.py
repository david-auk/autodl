import logging
import functions
import secret
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
	update.message.reply_text('Hi! Send /help to see the list of available commands.')
	user = update.message.from_user
	chat_id = update.message.from_user.id
	name = f"@{user.username}"
	if name == '@':
		name = user.first_name

	userExists = False
	for x in functions.getData('chatid', 'id', '=', chat_id):
		userExists = True

	if userExists:
		functions.chData('chatid', chat_id, 'name', name)
	else:
		functions.addChatIdData(name, chat_id, 'N/A', 'N/A')

def help(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('The following commands are available:\n/help - Show list of useful commands\n/passwd - Check password\n/latest - Ask for the latest data\n/info - Get info about a link')

def is_allowed_user(update, context):
	"""Check if the current user ID is allowed."""
	# Get the user ID
	chat_id = update.message.from_user.id

	# Check if the user ID is in the AllowedUserID variable
	userIsAllowed = False
	for (name, id, priority, authenticated) in functions.getData('chatid', 'id', '=', chat_id):
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

	keyboard = [[InlineKeyboardButton("10", callback_data='10'),InlineKeyboardButton("20", callback_data='20'),InlineKeyboardButton("30", callback_data='30')],[InlineKeyboardButton("Today", callback_data='today'),InlineKeyboardButton("Yesterday", callback_data='yesterday')]]

	reply_markup = InlineKeyboardMarkup(keyboard)

	update.message.reply_text('Please choose an option:', reply_markup=reply_markup)


def button_latest(update, context):
	"""Handle the button press."""
	query = update.callback_query
	query.answer()

	if query.data == '10':
		text = 'You selected 10.'
	elif query.data == '20':
		text = 'You selected 20.'
	elif query.data == '30':
		text = 'You selected 30.'
	elif query.data == 'today':
		text = 'You selected today.'
	elif query.data == 'yesterday':
		text = 'You selected yesterday.'
		
	query.edit_message_text(text=f"{text}")


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
			for (name, id, priority, authenticated) in functions.getData('chatid', 'id', '=', chat_id):
				userExists = True
				if priority == 'N/A':
					hasPriorityValue = True

			if userExists:
				functions.chData('chatid', chat_id, 'authenticated', '1')
				if hasPriorityValue:
					functions.chData('chatid', chat_id, 'priority', '3')
			else:
				functions.addChatIdData(name, chat_id, '3', '1')

			functions.msgHost(f"The user {name} just got added to the Datebase")

		else:
			context.bot.send_message(chat_id=chat_id, text="Sorry, that's not the correct password.")

	# Handle other messages as usual
	else:
		
		# Check if the user is allowed to use the bot
		if is_allowed_user(update, context) is False:
			context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, you are not authorized to use this bot.")
			return

#		print(message_text[20:28])

		if message_text[:7] == 'http://' or message_text[:8] == 'https://':
			if message_text[24:32] == 'watch?v=' or message_text[23:31] == 'watch?v=' or message_text[20:28] == 'watch?v=' or message_text[8:16] == 'youtu.be':
				vidId = functions.getVidId(message_text)
				context.bot.send_message(chat_id=chat_id, text=f"Thanks for the link, the vidID is: \'{vidId}\'")
			else:
				context.bot.send_message(chat_id=chat_id, text=f"Thanks for the link, this is not a youtube video link")
		else:
			context.bot.send_message(chat_id=chat_id, text="Sorry, that's not a valid link.")

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
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("passwd", check_password))
	dp.add_handler(CommandHandler("latest", ask_latest))
	dp.add_handler(CallbackQueryHandler(button_latest))
	dp.add_handler(CommandHandler("info", get_info))
	dp.add_handler(MessageHandler(Filters.text & (~Filters.command), link))
	dp.add_handler(MessageHandler(Filters.text & Filters.command, error))

	# Start the bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process is stopped
	updater.idle()

if __name__ == '__main__':
	main()