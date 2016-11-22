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

from db import db_session, User, Question, Survey
from datetime import date, datetime
from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
							TimedOut, ChatMigrated, NetworkError)
import telegram

import logging

import csv

import os.path

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, AGE, PHONE, SN, \
FEEL_TODAY, WHERE_ARE_YOU, ARE_YOU_HAPPY_NOW, \
FRESH_SELFY, FIRST_APP, \
SMART_SCREENSHOT, COLOR_YOU_LIKE = range(11)

u = User
q = Question
survey = Survey
# Добавить проверку на существование в photo: profile, selfy, screenshot
photo_dir='photo'
if os.path.isdir(photo_dir) == False:
	os.mkdir(photo_dir)
	os.mkdir(photo_dir + '/profile')
	os.mkdir(photo_dir + '/selfy')
	os.mkdir(photo_dir + '/screenshot')

if os.path.isfile('botdb.sqlite') == True:
	print('Db file exists')
# Загрузка вопросов из файла questions.txt в базу
# перенести в файл db и запускать 1 раз




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
		photo_file_name = 'photo/profile/' + str(update.message.from_user.id) + '.jpg'
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

	#db_session.add(q)
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
	else:
		gender = 3

	usr = update.message.from_user
	user = u.query.filter(User.id == update.message.from_user.id).first()
	user.gender = gender
	#print('u.gender =', u.gender)
	try:
		db_session.add(user)
		db_session.commit()
	except Exception as e:
		print(e)

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
	usr = u.query.filter(User.id == update.message.from_user.id).first()
	usr.phone = update.message.text
	db_session.add(usr)
	db_session.commit()
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
	usr = u.query.filter(User.id == update.message.from_user.id).first()
	usr.sn = update.message.text
	db_session.add(usr)
	db_session.commit()	

	user = update.message.from_user
	logger.info("SN account of %s: %s" % (user.first_name, update.message.text))

	return ConversationHandler.END

def skip_sn(bot, update):
	print(update.message.text)
	user = update.message.from_user
	logger.info("Bio of %s: %s" % (user.first_name, update.message.text))

	return ConversationHandler.END

#def feel_today(bot, update):
	
def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.')

	return ConversationHandler.END

def info(bot, update):
	#сделать проверку на наличие юзера в бд
	reply_keyboard = [['Хорошо'], ['Плохо'], ['Нормально']] 
	update.message.reply_text(
		'Привет! Я хочу задать тебе несколько вопросов. '
		'Как твое самочувствие сегодня?',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return FEEL_TODAY

def feel_today(bot, update):
	#reply_keyboard = [['скорее,да', 'да', 'скорее,нет', 'нет']]
	survey = Survey()
	dt_now = datetime.now()
	survey.answer_text = str(update.message.text)
	survey.answer_date = dt_now
	survey.user_id = update.message.from_user.id
	survey.question_id = 1
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
		'Где ты сейчас? Пришли мне геотег или нажми /skip, чтобы пропустить.')
		#reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))
	print('feel_today ends')
	return WHERE_ARE_YOU
	#return ARE_YOU_HAPPY_NOW

def where_are_you(bot, update):
	print('STATE WHERE_R_U')
	reply_keyboard = [['скорее,да'], ['да'], ['скорее,нет'], ['нет']]
	print(update.message.location)
	survey = Survey()
	dt_now = datetime.now()
	survey.answer_date = dt_now
	survey.question_id = 2
	survey.user_id = update.message.from_user.id
	survey.longitude = update.message.location['longitude']
	survey.latitude = update.message.location['latitude']
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
	'Ты счастливый сейчас?',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))	
	
	return ARE_YOU_HAPPY_NOW

def skip_where_are_you(bot, update):
	survey = Survey()
	reply_keyboard = [['скорее,да'], ['да'], ['скорее,нет'], ['нет']]
	dt_now = datetime.now()
	survey.answer_text = 'skip'
	survey.answer_date = dt_now
	survey.user_id = update.message.from_user.id
	survey.question_id = 3
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
	'Ты счастливый сейчас?',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))	

	return ARE_YOU_HAPPY_NOW	

def are_you_happy_now(bot, update):
	survey = Survey()
	dt_now = datetime.now()
	survey.answer_text = str(update.message.text)
	survey.answer_date = dt_now
	survey.user_id = update.message.from_user.id
	survey.question_id = 3
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
		'Пришли мне свежее селфи!')

	return FRESH_SELFY

def fresh_selfy(bot, update):
	survey = Survey()
	d_t_now = datetime.now()
	survey.user_id = update.message.from_user.id
	survey.question_id = 4
	survey.answer_date = d_t_now
	photo_file = bot.getFile(update.message.photo[-1].file_id)
	photo_file.download('photo/selfy/selfy_' + str(update.message.from_user.id) + '_' + str(d_t_now.strftime('%d.%m.%Y_%H:%M')) + '.jpg')
	survey.answer_photo = 'photo/selfy/selfy_' + str(update.message.from_user.id) + '_' + str(d_t_now.strftime('%d.%m.%Y_%H:%M')) + '.jpg'
	db_session.add(survey)
	db_session.commit()	
	reply_keyboard = [['Mail'],['Skype'],['Internet Browser'],['Facebook'],['Vkontakte'],['Odnoklassniki'],['Twitter']]
	update.message.reply_text(
		'Какое приложение на смартфоне ты открыл первым? '
		'Выбери один из предложенных вариантов или введи свой',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))
	return FIRST_APP

def first_app(bot, update):
	survey = Survey()
	dt_now = datetime.now()
	survey.answer_text = str(update.message.text)
	survey.user_id = update.message.from_user.id
	survey.question_id = 5
	survey.answer_date = dt_now
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
		'Пришли мне скриншот открытых приложения на твоем смартфоне.')
	
	return SMART_SCREENSHOT

def smart_screenshot(bot, update):
	survey = Survey()
	reply_keyboard = [['1','2','3','4','5','6','7','8','9']]
	dt_now = datetime.now()

	survey.user_id = update.message.from_user.id
	survey.question_id = 6
	survey.answer_date = dt_now
	db_session.add(survey)
	db_session.commit()	
	photo_file = bot.getFile(update.message.photo[-1].file_id)
	photo_file.download('photo/screenshot/screenshot_' + str(update.message.from_user.id) + '_' + str(dt_now.strftime('%d.%m.%Y_%H:%M')) + '.jpg')
	survey.answer_photo = 'photo/screenshot/screenshot_' + str(update.message.from_user.id) + '_' + str(dt_now.strftime('%d.%m.%Y_%H:%M')) + '.jpg'

	update.message.reply_text(
	'Какой цвет сейчас тебе больше нравится?',
			reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))
	
	return COLOR_YOU_LIKE


def color_you_like(bot, update):
	survey = Survey()
	dt_now = datetime.now()
	survey.user_id = update.message.from_user.id
	survey.question_id = 7
	survey.answer_date = dt_now
	survey.answer_text = str(update.message.text)
	db_session.add(survey)
	db_session.commit()	
	
	return ConversationHandler.END


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
		entry_points=[CommandHandler('start', start),
					CommandHandler('info', info)],
		#entry_points=[CommandHandler('ready', ready)],
# Добавить скип для локейшна и селфи

		states={
			GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],
			
			AGE: [MessageHandler(Filters.text, age),
					CommandHandler('skip', skip_age)],

			PHONE: [MessageHandler(Filters.text, phone),
						CommandHandler('skip', skip_phone)],

			SN: [MessageHandler(Filters.text, sn),
						CommandHandler('skip', skip_sn)],

			FEEL_TODAY: [MessageHandler(Filters.text, feel_today)],

			WHERE_ARE_YOU: [MessageHandler(Filters.location, where_are_you),
										CommandHandler('skip', skip_where_are_you)],

			ARE_YOU_HAPPY_NOW: [MessageHandler(Filters.text, are_you_happy_now)],

			FRESH_SELFY: [MessageHandler(Filters.photo, fresh_selfy)],

			FIRST_APP: [MessageHandler(Filters.text, first_app)],

			SMART_SCREENSHOT: [MessageHandler(Filters.photo, smart_screenshot)],

			COLOR_YOU_LIKE: [MessageHandler(Filters.text, color_you_like)]
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
