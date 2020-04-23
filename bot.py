# -*- coding: utf-8 -*-
import sys
import os
import time
from random import randint
import json
from utils import *
from botConfig import *
from cards import *
from language import *
import telebot
from telebot import apihelper
reload(sys)
sys.setdefaultencoding('utf-8')

appDir=os.path.abspath(os.path.dirname(__file__))
apihelper.proxy = telebotProxy
bot = telebot.TeleBot(botToken)

if not os.path.exists(appDir+"/db"):
	os.mkdir(appDir+"/db")
if not os.path.exists(appDir+"/db/users"):
	os.mkdir(appDir+"/db/users")
if not os.path.exists(appDir+"/db/games"):
	os.mkdir(appDir+"/db/games")

# Базы данных юзеров и игр находятся в классе Db в словарях db.user и db.game соответственно. После внесения важных изменений необходимо вызвать функцию db.save_user(message.chat.id) или db.save_game(message.chat.id) соответственно.
class Db():
	def __init__(self):
		self.userId=""
		self.chatId=""
		self.user={}
		self.game={}
	def load_user(self,userId):
		filename = appDir+"/db/users/"+str(userId)+".json"
		if os.path.isfile(filename):
				self.user[userId]=json.loads(fir(filename))
		try: self.user[userId]
		except KeyError: self.user[userId]={}
	def save_user(self,userId):
		filename = appDir+"/db/users/"+str(userId)+".json"
		if self.user[userId] and self.user[userId]!={} and self.user[userId]!="":
			fiw(filename,json.dumps(self.user[userId], indent=4))
	def load_game(self,userId):
		try: gameId=self.user[userId]["room"]
		except KeyError: return False
		if gameId!="":
			filename = appDir+"/db/games/"+str(gameId)+".json"
			if os.path.isfile(filename):
				self.game[gameId]=json.loads(fir(filename))
			try: self.game[gameId]
			except KeyError: self.game[gameId]={}
	def save_game(self,userId):
		try: gameId=self.user[userId]["room"]
		except KeyError: return False
		if gameId!="":
			filename = appDir+"/db/games/"+str(gameId)+".json"
			if self.game[gameId] and self.game[gameId]!={} and self.game[gameId]!="":
				fiw(filename,json.dumps(self.game[gameId], indent=4))

# Вся основная механика игры реализовывается в классе Game
class Game():
	def __init__(self):
		pass

def msg(chat,id,text="",lang=False):
	if lang==False: lang=db.user[chat]["lang"]
	bot.send_message(chat,txt[lang][id]+str(text),parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def main(message):
	db.load_user(message.chat.id)
	db.load_game(message.chat.id)
	try: db.user[message.chat.id]["lang"]
	except KeyError:
		msg(message.chat.id,"chooseLanguage",lang="default")
		bot.register_next_step_handler(message, change_language)
		return False
	if db.user[message.chat.id]["step"]=="main":
		if message.text=="/create":
			room=44
			while os.path.exists(appDir+"/db/games/"+str(room)+".json"):
				room=randint(10000,99999)
			db.user[message.chat.id]["step"]="created"
			db.user[message.chat.id]["room"]=str(room)
			db.save_user(message.chat.id)
			msg(message.chat.id,"chooseName")
			bot.register_next_step_handler(message, choose_name)
		elif message.text=="/join":
			msg(message.chat.id,"join")
			bot.register_next_step_handler(message, room_join)
		elif message.text=="/lang":
			msg(message.chat.id,"chooseLanguage",lang="default")
			bot.register_next_step_handler(message, change_language)
		else:
			msg(message.chat.id,"hello")
	elif db.user[message.chat.id]["step"]=="created":
		if message.text=="/game":
			db.game[db.user[message.chat.id]["room"]]["status"]="started"
			db.user[message.chat.id]["step"]="started"
			db.save_game(message.chat.id)
			db.save_user(message.chat.id)
			for player in db.game[db.user[message.chat.id]["room"]]["players"]:
				db.game[db.user[message.chat.id]["room"]]["status"]="started"
				msg(player,"gameStarted","\n".join(str(db.game[db.user[message.chat.id]["room"]]["nicknames"][str(v)]) for v in db.game[db.user[message.chat.id]["room"]]["players"]))
		elif message.text=="/cancel":
			db.user[message.chat.id]["step"]="main"
			db.user[message.chat.id]["room"]=""
			db.save_user(message.chat.id)
			msg(message.chat.id,"hello")
		else:
			msg(message.chat.id,"created")
	elif db.user[message.chat.id]["step"]=="joined":
		if db.game[db.user[message.chat.id]["room"]]["status"]=="started":
			db.user[message.chat.id]["step"]="started"
			db.save_user(message.chat.id)
			main(message)
		else:
			msg(message.chat.id,"joinedWait")
	elif db.user[message.chat.id]["step"]=="started":
		#тут начинается игра. Сообщение ниже высылаю для теста, можно удалить
		msg(message.chat.id,"chooseWinnerOrSkip")

def change_language(message):
	if message.text=="/en" or message.text=="/ru":
		db.user[message.chat.id]["lang"]=message.text.replace("/","")
		db.user[message.chat.id]["step"]="main"
		db.save_user(message.chat.id)
		msg(message.chat.id,"hello")
	else:
		msg(message.chat.id,"chooseLanguage",lang="default")
		bot.register_next_step_handler(message, change_language)

def room_join(message):
	if message.text=="/cancel":
		msg(message.chat.id,"hello")
	else:
		if not os.path.exists(appDir+"/db/games/"+str(message.text)+".json"):
			msg(message.chat.id,"join")
			bot.register_next_step_handler(message, room_join)
		else:
			db.user[message.chat.id]["step"]="joined"
			db.user[message.chat.id]["room"]=str(message.text)
			db.save_user(message.chat.id)
			msg(message.chat.id,"chooseName")
			bot.register_next_step_handler(message, choose_name)

def choose_name(message):
	db.user[message.chat.id]["nickname"]=str(message.text)
	if db.user[message.chat.id]["step"]=="created":
		db.game[db.user[message.chat.id]["room"]] = {"admin":message.chat.id,"players":[message.chat.id],"nicknames":{},"status":"preparing"}
	if db.user[message.chat.id]["step"]=="joined":
		db.load_game(message.chat.id)
		db.game[db.user[message.chat.id]["room"]]["players"].append(message.chat.id)
	db.game[db.user[message.chat.id]["room"]]["nicknames"][message.chat.id]=str(message.text)
	db.save_user(message.chat.id)
	db.save_game(message.chat.id)
	if db.user[message.chat.id]["step"]=="joined":
		msg(db.game[db.user[message.chat.id]["room"]]["admin"],"adminJoined",text=db.user[message.chat.id]["nickname"])
		msg(message.chat.id,"joined",db.user[message.chat.id]["room"])
		msg(message.chat.id,"joinedWait")
	if db.user[message.chat.id]["step"]=="created":
		msg(message.chat.id,"create",db.user[message.chat.id]["room"])
		msg(message.chat.id,"created")


if __name__ == "__main__":
	db=Db()
	game=Game()
	bot.polling(none_stop=True,interval=5,timeout=100)
'''while True:
	try:
		bot.polling(none_stop=True,interval=5,timeout=100)
	except Exception as e:
		logger.error(e)
		time.sleep(15)'''
