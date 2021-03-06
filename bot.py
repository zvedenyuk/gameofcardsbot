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
from cards import *
import random
from numpy import setdiff1d

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
stepsUser = {
    "main": "main",
    "created": "created",
    "joined": "joined",
    "started": "started",
    "": ""

}

statusGame = {
    "started": "started",
    "turn": "turn",
    "ended": "ended"

}


class Game():
    def __init__(self):
        self.playersNumber = 0
        self.wachterCounter = 0

#TODO: прикрутить в cancel сбора статистики: game_ended (score <10) or not_finished(cancel not pressed) or successful_ending (score >=10)
# Считаю, что room и nickname можно не чистить у юзера
    def end_game(self, message):
        db.load_game(message.chat.id)
        db.game[db.user[message.chat.id]["room"]]["status"] = statusGame["ended"]
        for player in db.game[db.user[message.chat.id]["room"]]["players"]:
            db.load_user(player)
            db.user[player]["step"] = "main"
            msg(player, "gameEnded")
            msg(player, "hello")
            db.save_user(player)
        db.save_game(message.chat.id)
        bot.register_next_step_handler(message, main)

    def update_wachter_counter(self):
        if self.wachterCounter == self.playersNumber:
            self.wachterCounter = 0
        else:
            self.wachterCounter += 1
        '''
        Кажется, это можно сделать проще и, не используя отдельную переменную self.playersNumber:

        self.wachterCounter=(self.wachterCounter+1)%len(db.game[db.user[message.chat.id]["room"]]["players"])
        '''
    def check_card_hands_trash(self, card_type):
        pass

    def create_hands(self, message):
        cardsOnHands = []
        for player in db.game[db.user[message.chat.id]["room"]]["players"]:
            availableWhiteCardsDeck = setdiff1d(cards["cah"]["white"], cardsOnHands)
            playerHand = random.sample(availableWhiteCardsDeck, 10)
            db.game[db.user[message.chat.id]["room"]]["hands"].update({player: playerHand})
            cardsOnHands.append(playerHand)
        db.save_game(message.chat.id)
        #TODO: add status to function in retur. Или включитьь логгирование. Интересно попробовать

    def show_my_hand(self, player):
        #TODO: shows hand of a player. Send player tg id
        pass

    def pick_black_card(self):
        pass

    def switch_black_card(self):
        pass

    def turn(self, message):
        if message.text == "/end_game":
            self.end_game(message)

        if message.text == "/black_card" and db.game[db.user[message.chat.id]["room"]]["status"] == statusGame["started"]:
            #Возможно, здесь можно не подгружать базы, так как мы их уже подгрузили в начале функции main(), а с этого момента не прошло много времени. Но если в дальнейшей логике предполагаются задержки, то ок, пусть будут
            db.load_game(message.chat.id)
            db.load_user(message.chat.id)

            db.game[db.user[message.chat.id]["room"]]["wachter"] = db.game[db.user[message.chat.id]["room"]]["players"][game.wachterCounter]
            self.create_hands(message)
            for player in db.game[db.user[message.chat.id]["room"]]["players"]:
                msg(player,"testMsg")
            #TODO: Прислать ведущему сообщение: вы теперь ведущий

            db.game[db.user[message.chat.id]["room"]]["status"] = statusGame["turn"]
            bot.register_next_step_handler(message, game.turn)

        if db.game[db.user[message.chat.id]["room"]]["status"] == statusGame["turn"]:
            pass

            # game.update_wachter_counter()


            # нужно дописать случай 1й раздачи
        #нужно описать случай обычной раздачи






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
                #TODO: nicknames - пользователя (ключ словаря) нужно оставить в int
                msg(player,"gameStarted","\n".join(str(db.game[db.user[message.chat.id]["room"]]["nicknames"][str(v)]) for v in db.game[db.user[message.chat.id]["room"]]["players"]))
            game.playersNumber = len(db.game[db.user[message.chat.id]["room"]]["players"])
            main(message)

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
        msg(message.chat.id, "firstTable")
        bot.register_next_step_handler(message, game.turn)

def change_language(message):
    if message.text=="/en" or message.text=="/ru":
        db.user[message.chat.id]["lang"]=message.text.replace("/","")
        db.user[message.chat.id]["step"]="main"
        db.save_user(message.chat.id)
        msg(message.chat.id,"hello")
    else:
        msg(message.chat.id,"chooseLanguage", lang="default")
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
        db.game[db.user[message.chat.id]["room"]] = {"admin": message.chat.id, "players": [message.chat.id], "scores": {}, "nicknames": {}, "status": "preparing", "wachter": None, "turn":None, "table": {"black": None, "white": []}, "hands": {}, "trashWhite": [], "trashBlack": []}
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
