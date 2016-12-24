#!/usr/bin/env python
# -*- coding: utf-8 -*-

# /start - как зовут и берет данные из профиля
# /info - остальные вопросы
# /help - usage

from db import db_session, User, Question, Survey

from datetime import date, datetime

from telegram import ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, \
							ConversationHandler
from telegram.error import TelegramError, Unauthorized, BadRequest, \
							TimedOut, ChatMigrated, NetworkError

from roken import roken

import telegram

import logging

import csv

import os.path

import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, AGE, PHONE, SN, \
FEEL_TODAY, WHERE_ARE_YOU, ARE_YOU_HAPPY_NOW, \
FRESH_SELFY, FIRST_APP, SMART_SCREENSHOT, \
COLOR_YOU_LIKE, NAME, CUR_MOOD, SMOKE, SPORT, \
NEWS, COSMETIC_ASK, COSMETIC_IF, COSMETIC_ANSWER,\
HAPPY_NEW_YEAR, COSMETIC_GEO, COSMETIC_KEY = range(22)

u = User
q = Question
survey = Survey

photo_dir='photo'
if os.path.isdir(photo_dir) == False:
	os.mkdir(photo_dir)
	os.mkdir(photo_dir + '/profile')
	os.mkdir(photo_dir + '/selfy')
	os.mkdir(photo_dir + '/screenshot')
	os.mkdir(photo_dir + '/cosmetic')

if os.path.isfile('botdb.sqlite') == True:
	print('Db file exists')

with open('questions.txt', 'r') as f:

	fields = ['question_text']
	reader = csv.DictReader(f, fields, delimiter='\n')
	for row in reader:
		q = Question(question_text=row['question_text'])
		db_session.add(q)
		db_session.commit()




def start(bot, update):
	q = Question()

	user = u.query.filter(User.id == update.message.from_user.id).first()
	if user is None:
		user = User()
		user.id = int(update.message.from_user.id)
		profile_photo = bot.getUserProfilePhotos(user.id)
		user.chat_id = int(update.message.chat_id)
		user.username = update.message.from_user.username
		pphoto=bot.getFile(profile_photo['photos'][0][-1]['file_id'])
		# %s {} .format
		photo_file_name = 'photo/profile/' + str(update.message.from_user.id) + '.jpg'
		pphoto.download(photo_file_name)
		user.profile_photo = photo_file_name
		update.message.reply_text(
		'Привет! Как тебя зовут? ')

	else:
		update.message.reply_text('Привет, мы знакомы. Нажми /info, чтобы пройти опрос.')
		return ConversationHandler.END

	db_session.add(user)
	db_session.commit()

	return NAME

def name(bot, update):
	name = update.message.text
	user = u.query.filter(User.id == update.message.from_user.id).first()
	user.name = name
	user.first_date = datetime.now()
	try:
		db_session.add(user)
		db_session.commit()
	except Exception as e:
		print(e)

	update.message.reply_text('Привет, %s! ' % name)
	update.message.reply_text('Я QBot. Буду спрашивать тебя обо всем. \
							Теперь можно нажать /info и перейти к интервью.')
	return ConversationHandler.END


def gender(bot, update):
	if update.message.text == 'Мальчик':
		gender = 0
	elif update.message.text == 'Девочка':
		gender = 1
	else:
		gender = 3

	usr = update.message.from_user
	user = u.query.filter(User.id == update.message.from_user.id).first()
	user.gender = gender

	try:
		db_session.add(user)
		db_session.commit()
	except Exception as e:
		print(e)

	logger.info("Gender of %s: %s" % (usr.first_name, update.message.text))
	update.message.reply_text('Спасибо! Теперь пришли дату рождения, '
				
							  'или нажми /skip, чтобы пропустить вопрос.')

	return AGE

def age(bot, update):
	print('State age')
	user = u.query.filter(User.id == update.message.from_user.id).first()
	print(user)
	user.birthdate = datetime.strptime(update.message.text, '%d.%m.%Y')
	print(user.birthdate)
	db_session.add(user)
	db_session.commit()
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
	user = update.message.from_user
	user_phone = update.message.text
	usr = u.query.filter(User.id == update.message.from_user.id).first()
	usr.phone = update.message.text
	db_session.add(usr)
	db_session.commit()
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


def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.')

	return ConversationHandler.END

def info(bot, update):
	user = u.query.filter(User.id == update.message.from_user.id).first()
	if user is None:
		update.message.reply_text('Привет, давай познакомимся! '
			'Пожалуйста, нажми /start и представься боту)')
		return ConversationHandler.END

	reply_keyboard = [['Хорошо', 'Плохо', 'Нормально']] 
	update.message.reply_text(
		'Привет! Я хочу задать тебе несколько вопросов. '
		'Как твое самочувствие сегодня?',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	print('ends info')
	return FEEL_TODAY

def feel_today(bot, update):
	reply_keyboard = [['Хорошее', 'Плохое', 'Нормальное']]
	print(update.message)
	survey = Survey()
	dt_now = datetime.now()
	survey.answer_text = str(update.message.text)
	survey.answer_date = dt_now
	survey.user_id = update.message.from_user.id
	survey.question_id = 1
	if survey.answer_text in reply_keyboard[0]:
		db_session.add(survey)
		db_session.commit()	
	update.message.reply_text(
		'Какое у тебя настроение?',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
	print('feel_today ends')
	return CUR_MOOD

def cur_mood(bot, update):
	survey = Survey()
	dt_now = datetime.now()
	survey.answer_text = str(update.message.text)
	survey.answer_date = dt_now
	survey.user_id = update.message.from_user.id
	survey.question_id = 2
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
		'Где ты сейчас? Пришли мне геотег или нажми /skip, чтобы пропустить.')
	return WHERE_ARE_YOU

def where_are_you(bot, update):
	reply_keyboard = [['1','2','3'],['4','5','6'],['7','8','9']]
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
	'Какой цвет сейчас тебе больше нравится?',
			reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))
	
	return COLOR_YOU_LIKE

def skip_where_are_you(bot, update):
	survey = Survey()
	reply_keyboard = [['1','2','3'],['4','5','6'],['7','8','9']]
	dt_now = datetime.now()
	survey.answer_text = 'skip'
	survey.answer_date = dt_now
	survey.user_id = update.message.from_user.id
	survey.question_id = 3
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
	'Какой цвет сейчас тебе больше нравится?',
			reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))

	return COLOR_YOU_LIKE	

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
	#question_id берется из бд
	survey.question_id = 5
	survey.answer_date = dt_now
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(
		'Пришли мне скриншот открытых приложения на твоем смартфоне.')
	
	return SMART_SCREENSHOT

def smart_screenshot(bot, update):
	survey = Survey()
	reply_keyboard = [['1','2','3'],['4','5','6'],['7','8','9']]
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

def help(bot, update):
	update.message.reply_text('/start - знакомство с ботом. /info - запустить опрос.')
	return ConversationHandler.END	
def ask(bot, update):
	question_text = '''
		Я хочу спросить тебя о том, как ты живешь.

		Прошу тебя сегодня весь день сегодня присылать геометку в месте, где\
		ты куришь. Если ты не куришь, тогда посылай метку, где видишь курящих\
		людей. Присылай	метку и пиши, что это за место (в подъезде, рядом с\
		офисом, в кафе, другое).

		'''
	update.message.reply_text(question_text)
	return SMOKE

def smoke(bot, update):
	question_text = '''
		Здорово! А ты спортом занимаешься? Если ответ да, тогда следующий вопрос.\
		Прошу тебя сегодня весь день сегодня присылать геометку в месте, где ты\
		занимаешься спортом (или любой физической активностью). Присылай метку и\
		пиши, что это ты делаешь(в парке, в зале, на улицах города, за городом,\
		другое) /skip пропустить вопрос.
		'''
	survey = Survey()
	dt_now = datetime.now()
	survey.user_id = update.message.from_user.id
	survey.question_id = 7
	survey.answer_date = dt_now
	survey.answer_text = str(update.message.text)
	survey.longitude = update.message.location['longitude']
	survey.latitude = update.message.location['latitude']
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(question_text)
	return SPORT

def sport(bot, update):
	question_text = '''
		Спрошу тебя о новостях. Пришли мне геометку сегодня в тот момент,\
		когда узнаешь важную для себя новость. И обязательно напиши, что\
		это за новость и откуда ты ее узнал?
		'''
	survey = Survey()
	dt_now = datetime.now()
	survey.user_id = update.message.from_user.id
	survey.question_id = 7
	survey.answer_date = dt_now
	survey.answer_text = str(update.message.text)
	db_session.add(survey)
	db_session.commit()	
	update.message.reply_text(question_text)
	return NEWS

def news(bot, update):
	survey = Survey()
	dt_now = datetime.now()
	survey.user_id = update.message.from_user.id
	survey.question_id = 7
	survey.answer_date = dt_now
	survey.answer_text = str(update.message.text)
	db_session.add(survey)
	db_session.commit()	
	return ConversationHandler.END

def happy_new_year(bot, update):
	question_text = '''
		Где вы будете отмечать новый год?
		'''
	update.message.reply_text(question_text)
	return COSMETIC_ASK

def cosmetic_ask(bot, update):
	question_text = '''
		Планируете ли вы купить себе косметику в ближайшие две недели (помаду, тушь или что-то ещё)?
		'''
	update.message.reply_text(question_text)
	return COSMETIC_IF
	
def cosmetic_if(bot, update):
	if str((update.message.text).lower()) == 'да':
		question_text = '''
			Присылайте фотографии и гео-метки каждый раз,\
		когда думаете о помаде/туши и других средствах для макияжа\
		и когда видите какую-то информацию о средствах для макияжа.
			'''
		update.message.reply_text(question_text)
		return COSMETIC_ANSWER
	else:
		print("NO")
	print('cosmetic_if OK')
	return ConversationHandler.END

def cosmetic_answer(bot, update):
	survey = Survey()
	dt_now = datetime.now()
	survey.user_id = update.message.from_user.id
	survey.question_id = 7
	survey.answer_date = dt_now
	survey.answer_text = str(update.message.text)
	photo_file = bot.getFile(update.message.photo[-1].file_id)
	photo_name = 'photo/cosmetic/cosm_' + str(update.message.from_user.id) + '_' + str(dt_now.strftime('%d.%m.%Y_%H:%M')) + '.jpg'
	photo_file.download(photo_name)
	survey.answer_photo = photo_name
	print(update.message.text)
	question_text = '''
			Спасибо! Теперь пришли, пожалуйста, геометку\
			где сделана эта фотография.
			'''
	update.message.reply_text(question_text)
	#survey.longitude = update.message.location['longitude']
	#survey.latitude = update.message.location['latitude']
	#survey.longitude = update.message.location['longitude']
	#survey.latitude = update.message.location['latitude']
	db_session.add(survey)
	db_session.commit()	
	return COSMETIC_GEO

def cosmetic_key(bot, update):
	#brand1_btn = KeyboardButton('Brand1', request_location=True)
	#brand2_btn = KeyboardButton('Brand2', request_location=True)
	#brand3_btn = KeyboardButton('Brand3', request_location=True)
	brand1_btn = KeyboardButton('Brand1')
	brand2_btn = KeyboardButton('Brand2')
	brand3_btn = KeyboardButton('Brand3')
	reply_keyboard = [[brand1_btn],[brand2_btn],[brand3_btn]]
	update.message.reply_text(
	'Какой бренд сейчас тебе больше нравится?')

	#		reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard=True))
	print('COSMETIC KEY')
	return COSMETIC_ANSWER

def cosmetic_geo(bot, update):
	survey = Survey()
	dt_now = datetime.now()
	survey.user_id = update.message.from_user.id
	survey.question_id = 7
	survey.answer_date = dt_now
	survey.longitude = update.message.location['longitude']
	survey.latitude = update.message.location['latitude']
	db_session.add(survey)
	db_session.commit()
	print(update.message)
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
		
def main():
	# MyQ bot
	#updater = Updater("265721672:AAF2PZz-LI5O1F2P_hiOe5AvMR-g19bwYGk")
	updater = Updater(roken)
	dp = updater.dispatcher

	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start),
					CommandHandler('info', info),
					CommandHandler('ask', ask),
					CommandHandler('happy_new_year', happy_new_year),
					CommandHandler('help', help)],

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

			COLOR_YOU_LIKE: [MessageHandler(Filters.text, color_you_like)],

			NAME: [MessageHandler(Filters.text, name)],

			CUR_MOOD: [MessageHandler(Filters.text, cur_mood)],

			SMOKE: [MessageHandler(Filters.text, smoke)],

			SPORT: [MessageHandler(Filters.text, sport)],

			NEWS: [MessageHandler(Filters.text, news)],

			COSMETIC_ASK: [MessageHandler(Filters.text, cosmetic_ask)],

			COSMETIC_IF: [MessageHandler(Filters.text, cosmetic_if)],

			COSMETIC_ANSWER: [MessageHandler(Filters.all, cosmetic_answer)],

			COSMETIC_GEO: [MessageHandler(Filters.location, cosmetic_geo)],

			COSMETIC_KEY: [MessageHandler(Filters.all, cosmetic_key)]

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
