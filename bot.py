# -*- coding: utf-8 -*-
import sys
import os
import time
import logging
from botConfig import *
from cards import *
from language import *
import telebot
from telebot import apihelper
reload(sys)
sys.setdefaultencoding('utf-8')

appDir=os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger('GoC')
c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(asctime)s %(levelname)-7s %(funcName)15s:%(lineno)3d ☄️  %(message)s',"%d.%m %H:%M:%S")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)
logger.setLevel(logging.DEBUG)

apihelper.proxy = telebotProxy
bot = telebot.TeleBot(botToken)

@bot.message_handler(content_types=['text'])
def main(message):
    if not os.path.exists(appDir+"/db/users/"+str(message.from_user.id)+".json"):
        bot.send_message(message.chat.id,txt["default"]["chooseLanguage"],parse_mode= "Markdown")
        bot.register_next_step_handler(message, hello)
    if message.text=="/hey":
        print "ping"
        bot.send_message(message.chat.id,"*Hi!*",parse_mode="Markdown")

def hello(message):
    print message.from_user.id
    print message.chat.id
    if message.text=="/eng" or  message.text=="/rus":
        bot.send_message(message.chat.id,message.from_user.id)
    else:
        bot.send_message(message.chat.id,txt["default"]["chooseLanguage"],parse_mode= "Markdown")
        bot.register_next_step_handler(message, hello)

while True:
	try:
		bot.polling(none_stop=True,interval=5,timeout=100)
	except Exception as e:
		logger.error(e)
		time.sleep(15)
