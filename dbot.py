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

from db import db_session, User, Question
from datetime import date, datetime
from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
							TimedOut, ChatMigrated, NetworkError)
import telegram

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, AGE, PHONE, SN = range(4)

u = User
q = Question

def start(bot, update):
	q = Question()
	reply_keyboard = [['Boy', 'Girl', 'Other']]
	user = u.query.filter(User.id == update.message.from_user.id).first()
	if user is None:
		user = User()
		user.id = int(update.message.from_user.id)
		profile_photo = bot.getUserProfilePhotos(user.id)
		user.chat_id = int(update.message.chat_id)
		user.username = update.message.from_user.username
		pphoto=bot.getFile(profile_photo['photos'][0][-1]['file_id'])
		photo_file_name = 'photo/' + str(update.message.from_user.id) + '.jpg'
		pphoto.download(photo_file_name)
		user.profile_photo = photo_file_name
		if bot.get_chat(update.message.chat_id)['type'] == 'group':
				for admin in bot.get_chat_administrators(chat_id=update.message.chat_id):
					if admin.user.id == user.id:
						user.is_admin = True
					else: 
						user.is_admin = False

	else: 
		print("Привет, мы знакомы.")

	db_session.add(q)
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
	logger.info("Gender of %s: %s" % (usr.first_name, update.message.text))
	update.message.reply_text('I see! Please send me your birthdate, '
							  'so I know how old are you, or send /skip if you don\'t want to.')

	return AGE

def age(bot, update):
	print('State age')
	user = u.query.filter(User.id == update.message.from_user.id).first()
	print(user)
	user.birthdate = datetime.strptime(update.message.text, '%d.%m.%Y')
	print(user.birthdate)
	db_session.add(user)
	db_session.commit()
	#usr = update.message.from_user
	#logger.info("Birthday of %s: %s" % (usr.first_name, update.message.text))
	print(user.birthdate)
	update.message.reply_text('Now, send me phone number please, '
							  'or send /skip.')
	return PHONE


def skip_age(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a birthdate." % user.first_name)
	update.message.reply_text('Now, send me phone number please, '
							  'or send /skip.')

	return PHONE

def phone(bot, update):
	print('PHONE state')
	print(update.message.text)
	user = update.message.from_user
	user_phone = update.message.text
	#print(update.message.location)
	logger.info("Phone number of %s: %s"
				% (user.first_name, update.message.text))
	update.message.reply_text('Maybe I\'ll call you sometime! '
							  'Show me your best photos! Send me a link to your instagram account.')

	return SN

def skip_phone(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a phone number." % user.first_name)
	update.message.reply_text('You seem a bit paranoid! '
							  'Show me your best photos! Send me a link to your instagram account.')

	return SN

def sn(bot, update):
	print(update.message.text)
	user = update.message.from_user
	logger.info("SN account of %s: %s" % (user.first_name, update.message.text))

	return ConversationHandler.END

def skip_sn(bot, update):
	print(update.message.text)
	user = update.message.from_user
	logger.info("Bio of %s: %s" % (user.first_name, update.message.text))

	return ConversationHandler.END

def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.')

	return ConversationHandler.END

#def error(bot, update, error):
#	logger.warn('Update "%s" caused error "%s"' % (update, error))

def error_callback(bot, update, error):
	try:
		raise error
	#except Unauthorized:
		# remove update.message.chat_id from conversation list
	except BadRequest as a:
		print(a)
		# handle malformed requests - read more below!
	except TimedOut as t:
		print(t)
		# handle slow connection problems
	except NetworkError as n:
		print(n)
		# handle other connection problems
	#except ChatMigrated as e:
		# the chat_id of a group has changed, use e.new_chat_id instead
	except TelegramError as ter:
		print(ter)
		# handle all other telegram related errors
		
def main():
	# MyQ bot
	updater = Updater("265721672:AAF2PZz-LI5O1F2P_hiOe5AvMR-g19bwYGk")

	dp = updater.dispatcher

	# Add conversation handler with the states GENDER, AGE, PHONE, SN
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],
		#entry_points=[CommandHandler('ready', ready)],

		states={
			GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],
			
			AGE: [MessageHandler([Filters.text], age),
					CommandHandler('skip', skip_age)],

			PHONE: [MessageHandler([Filters.text], phone),
						CommandHandler('skip', skip_phone)],

			SN: [MessageHandler([Filters.text], sn),
						CommandHandler('skip', skip_sn)]

			#SENDM: [sendm]
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)



	# log all errors
	dp.add_error_handler(error_callback)

	# Start the Bot
	updater.start_polling()

	# Run the bot until the you presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
