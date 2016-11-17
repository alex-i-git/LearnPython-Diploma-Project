#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from db import db_session, User
from datetime import date, datetime
from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
import telegram

import logging



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO, AGE, COMMIT = range(6)

u = User

def talk_to_me(bot, update):
	user_input = (((update.message.text).lower()).rstrip()).lstrip()
	print(user_input)

def start(bot, update):
	reply_keyboard = [['Boy', 'Girl', 'Other']]
	user = u.query.filter(User.id == update.message.from_user.id).first()
	
	if user is None:
		user = User()
		print(user)
		user.id = int(update.message.from_user.id)
		user.chat_id = int(update.message.chat_id)
		user.username = update.message.from_user.username
		db_session.add(user)
		db_session.commit()

	update.message.reply_text(
		'Hi! My name is Professor Bot. I will hold a conversation with you. '
		'Send /cancel to stop talking to me.\n\n'
		'Are you a boy or a girl?',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return GENDER


def gender(bot, update):
	if update.message.text == 'Boy':
		gender = 0
	elif update.message.text == 'Girl':
		gender = 1

	usr = update.message.from_user
	user = u.query.filter(User.id == update.message.from_user.id).first()
	user.gender = gender
	#print('u.gender =', u.gender)
	db_session.add(user)
	db_session.commit()
	#user_data['gender'] = gender
	#user = update.message.from_user
	#u = User(gender)
	#db_session.add(u)
	#db_session.commit()
	logger.info("Gender of %s: %s" % (usr.first_name, update.message.text))
	update.message.reply_text('I see! Please send me a photo of yourself, '
							  'so I know what you look like, or send /skip if you don\'t want to.')

	return PHOTO


def photo(bot, update):
	user = u.query.filter(User.id == update.message.from_user.id).first()
	file_name = 'photo/' + str(update.message.from_user.id) + '.jpg'
	user.photo=file_name
	db_session.add(user)
	db_session.commit()
	print(update.message.text)
	user = update.message.from_user
	print(type(update.message.photo))
	print(update.message.photo)
	photo_file = bot.getFile(update.message.photo[-1].file_id)
	photo_file.download(file_name)
	logger.info("Photo of %s: %s" % (user.first_name, 'user_photo.jpg'))
	update.message.reply_text('Gorgeous! Now, send me your location please, '
							  'or send /skip if you don\'t want to.')

	return LOCATION


def skip_photo(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a photo." % user.first_name)
	update.message.reply_text('I bet you look great! Now, send me your location please, '
							  'or send /skip.')

	return LOCATION


def location(bot, update):
	print(update.message.text)
	user = update.message.from_user
	user_location = update.message.location
	print(update.message.location)
	logger.info("Location of %s: %f / %f"
				% (user.first_name, user_location.latitude, user_location.longitude))
	update.message.reply_text('Maybe I can visit you sometime! '
							  'At last, tell me something about yourself.')

	return BIO


def skip_location(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a location." % user.first_name)
	update.message.reply_text('You seem a bit paranoid! '
							  'At last, tell me something about yourself.')

	return BIO


def bio(bot, update):
	print(update.message.text)
	user = update.message.from_user
	logger.info("Bio of %s: %s" % (user.first_name, update.message.text))
	update.message.reply_text('Please, enter your birthdate in dd.mm.yyyy format.')

	return AGE

def age(bot, update):
	print(update.message.text)
	u.birthdate = datetime.strptime(update.message.text, '%d.%m.%Y')
	db_session.commit()
	print(u.birthdate)
	user = update.message.from_user
	logger.info("Age of %s: %s" % (user.first_name, update.message.text))

	
	#db_session.commit()

	return COMMIT

def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.')

	return ConversationHandler.END


def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def commit():
	

	return ConversationHandler.END


def main():
	# MyQ bot
	updater = Updater("265721672:AAF2PZz-LI5O1F2P_hiOe5AvMR-g19bwYGk")

	

	# lp_chat bot
	#updater = Updater("291897611:AAGKsBmX9pt3mi2FiMzVEzf6V2ErIrjiK5k")

	#Отправка сообщения по chat_id
	#bot = telegram.Bot("265721672:AAF2PZz-LI5O1F2P_hiOe5AvMR-g19bwYGk")
	#u = User
	#for id in u.query.all():
	#	print(id.chat_id)
	#	bot.sendMessage(id.chat_id,'Сообщение от бота')

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	dp.add_handler(MessageHandler([Filters.text], talk_to_me))

	# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],
		#entry_points=[CommandHandler('ready', ready)],

		states={
			GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],
			
			PHOTO: [MessageHandler([Filters.photo], photo),
					CommandHandler('skip', skip_photo)],

			LOCATION: [MessageHandler([Filters.location], location),
					   CommandHandler('skip', skip_location)],

			BIO: [MessageHandler([Filters.text], bio)],

			AGE: [MessageHandler([Filters.text], age)],

			COMMIT: [commit]
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)



	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until the you presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
