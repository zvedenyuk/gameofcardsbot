# -*- coding: utf-8 -*-
import sys
import os
import time
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

class Db():
	def __init__(self):
		self.userId=""
		self.chatId=""
		self.user={}
		self.gameId=""
		self.game={}
	def db_load_user(self):
		if self.userId!="":
			filename = appDir+"/db/users/"+str(self.userId)+".json"
			if os.path.isfile(filename):
					self.user=json.loads(fir(filename))
			if not self.user: self.user={}
	def db_save_user(self):
		if self.userId!="":
			filename = appDir+"/db/users/"+str(self.userId)+".json"
			if self.user and self.user!="":
				fiw(filename,json.dumps(self.user, indent=4))

def msg(id,text=""):
	bot.send_message(db.chatId,txt[db.user["lang"]][id]+str(text),parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def main(message):
	if db.userId=="": db.userId=message.from_user.id
	if db.chatId=="": db.chatId=message.chat.id
	db.db_load_user()
	try: db.user["lang"]
	except KeyError:
		bot.send_message(message.chat.id,"*log1* "+str(message.text),parse_mode="Markdown")
		bot.send_message(message.chat.id,txt["default"]["chooseLanguage"],parse_mode= "Markdown")
		bot.register_next_step_handler(message, hello)
		return False
	if db.user["step"]=="main":
		if message.text=="/create":
			msg("create",2423523)
		elif message.text=="/join":
			msg("join")
	if message.text=="/hey":
		print "ping"
		bot.send_message(message.chat.id,"*Hi!*",parse_mode="Markdown")

def hello(message):
	if message.text=="/en" or  message.text=="/ru":
		db.user["lang"]=message.text.replace("/","")
		db.user["step"]="main"
		msg("hello")
	else:
		bot.send_message(message.chat.id,"*log2* "+message.text,parse_mode="Markdown")
		bot.send_message(message.chat.id,txt["default"]["chooseLanguage"],parse_mode= "Markdown")
		bot.register_next_step_handler(message, hello)

if __name__ == "__main__":
	db=Db()
	bot.polling(none_stop=True,interval=5,timeout=100)
'''while True:
	try:
		bot.polling(none_stop=True,interval=5,timeout=100)
	except Exception as e:
		logger.error(e)
		time.sleep(15)'''
