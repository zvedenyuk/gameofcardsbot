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

# Базы данных юзера и игры находятся в классе Db в словарях db.user и db.game соответственно. После внесения важных изменений необходимо вызвать функцию db.save_user() или db.load_game() соответственно.
class Db():
	def __init__(self):
		self.userId=""
		self.chatId=""
		self.user={}
		self.game={}
	def load_user(self):
		if self.userId!="":
			filename = appDir+"/db/users/"+str(self.userId)+".json"
			if os.path.isfile(filename):
					self.user=json.loads(fir(filename))
			if not self.user: self.user={}
	def save_user(self):
		if self.userId!="":
			filename = appDir+"/db/users/"+str(self.userId)+".json"
			if self.user and self.user!={} and self.user!="":
				fiw(filename,json.dumps(self.user, indent=4))
	def load_game(self):
		if self.user["room"]!="":
			filename = appDir+"/db/games/"+str(self.user["room"])+".json"
			if os.path.isfile(filename):
					self.game=json.loads(fir(filename))
			if not self.game: self.game={}
	def save_game(self):
		if self.user["room"]!="":
			filename = appDir+"/db/games/"+str(self.user["room"])+".json"
			if self.game and self.game!={} and self.game!="":
				fiw(filename,json.dumps(self.game, indent=4))

# Вся основная механика игры реализовывается в классе Game
class Game():
	def __init__(self):
		pass

def msg(id,text="",chat=False,lang=False):
	if chat==False: chat=db.chatId
	if lang==False: lang=db.user["lang"]
	bot.send_message(db.chatId,txt[lang][id]+str(text),parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def main(message):
	if db.userId=="": db.userId=message.from_user.id
	if db.chatId=="": db.chatId=message.chat.id
	db.load_user()
	db.load_game()
	try: db.user["lang"]
	except KeyError:
		bot.send_message(message.chat.id,"*log1* "+str(message.text),parse_mode="Markdown")
		msg("chooseLanguage",lang="default")
		bot.register_next_step_handler(message, change_language)
		return False
	if message.text=="/hey":
		print "ping"
		bot.send_message(message.chat.id,"*Hi!*",parse_mode="Markdown")
	elif db.user["step"]=="main":
		if message.text=="/create":
			room=44
			while os.path.exists(appDir+"/db/games/"+str(room)+".json"):
				room=randint(10000,99999)
			db.user["step"]="created"
			db.user["room"]=str(room)
			db.game={"admin":db.userId,"players":[db.userId],"status":"preparing"}
			db.save_game()
			db.save_user()
			msg("create",room)
			msg("created")
		elif message.text=="/join":
			msg("join")
			bot.register_next_step_handler(message, room_join)
		elif message.text=="/lang":
			msg("chooseLanguage",lang="default")
			bot.register_next_step_handler(message, change_language)
		else:
			msg("hello")
	elif db.user["step"]=="created":
		if message.text=="/game":
			db.game["status"]="started"
			db.save_game()
			for player in db.game["players"]:
				db.game["status"]="started"
				msg("gameStarted","\n".join(str(v) for v in db.game["players"]))
		elif message.text=="/cancel":
			db.user["step"]="main"
			db.user["room"]=""
			db.save_user()
			msg("hello")
		else:
			msg("created")
	elif db.user["step"]=="joined":
		msg("joined")

def change_language(message):
	if message.text=="/en" or message.text=="/ru":
		db.user["lang"]=message.text.replace("/","")
		db.user["step"]="main"
		db.save_user()
		msg("hello")
	else:
		bot.send_message(message.chat.id,"*log2* "+message.text,parse_mode="Markdown")
		msg("chooseLanguage",lang="default")
		bot.register_next_step_handler(message, change_language)

def room_join(message):
	if message.text=="/cancel":
		msg("hello")
	else:
		if not os.path.exists(appDir+"/db/games/"+str(message.text)+".json"):
			msg("join")
			bot.register_next_step_handler(message, room_join)
		else:
			db.user["step"]="joined"
			db.user["room"]=str(message.text)
			db.save_user()
			db.load_game()
			db.game["players"].append(message.from_user.id)
			db.save_game()
			msg("adminJoined",text="@"+str(message.from_user.username),chat=db.game["admin"])
			msg("joined",message.text)

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
