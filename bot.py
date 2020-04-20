# -*- coding: utf-8 -*-
import sys
import os
import time
from botConfig import *
import telebot
from telebot import apihelper
reload(sys)
sys.setdefaultencoding('utf-8')

appDir=os.path.abspath(os.path.dirname(__file__))

apihelper.proxy = telebotProxy
bot = telebot.TeleBot(botToken)

@bot.message_handler(content_types=['text'])
def main(message):
    if message.text=="/hey":
        print "ping"
        bot.send_message(message.chat.id,"*Hi!*",parse_mode="Markdown")

while True:
	try:
		bot.polling(none_stop=True,interval=5,timeout=100)
	except Exception as e:
		print e
		time.sleep(15)
