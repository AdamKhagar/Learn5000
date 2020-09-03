import telebot
import json
from admin import Admin
from template import Template
from datetime import datetime
from config import profiles, languages, send_time_var, feed_answers
from secret import token, admin_token
from time import strftime, sleep
from user import User
from words import Words
from feedback import *
from threading import Thread

bot = telebot.TeleBot(token)
admin_bot = telebot.TeleBot(admin_token)

keyboard_off = telebot.types.ReplyKeyboardRemove()

def try_send(user_id, text, keyboard=None):
    '''does the same telebot.send_message() and deletes data from locked chats'''
    try:
        bot.send_message(user_id, text, reply_markup=keyboard)
    except telebot.apihelper.ApiException:
        user = User(user_id)
        print(f'delete user#{user_id}')
        user.del_user()

def send_messages(users):
    i = 0 
    for u in users:
        user = User(u)
        if user.get_time() == time_zone() and user.get_last_day() != strftime('%x'):
            # message limitation 
            #
            # this is necessary because telegram api 
            # limits us to 30 messages per second
            # in addition, we have other threads that 
            # also need to respond to user requests
            # so I set a limit of 10 messages per second
            # from this thread
            if i == 5:
                i = 0
                sleep(1)
            user.set_last_day()
            if user.check_data() == 'data error':
                # data error
                i += 1
                print('problem_data')
                print(u)
                try_send(u, Template.data_error())

            elif user.check_data() == 'no await':
                # no message waiting
                print('no message waiting')
                print(u)

            elif user.check_data() == 'good':
                # all rigtht
                i += 1
                w = Words(user)
                words = w.get_words()
                print('ok')

                try_send(u, words)
    else:
        sleep(5*60)

def time_zone():
    ''' возвращает номер профиль для отправки сообщений по времени '''
    for key, value in profiles.items():
        start = datetime.strptime(value[0], '%X')
        end = datetime.strptime(value[1], '%X')
        if time_in_range(start.time(), end.time()):
            return key

    return False

def time_in_range(start, end):
    ''' проверяет находится ли текущее время в промежутке от start до end'''
    x = datetime.today().time()
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def sender():
    while True:  
        if time_zone() != False:
            print('send') 
            send_messages(User.users_list())
        else:
            print('not time')
            sleep(10*60)

@admin_bot.message_handler(commands=['send'],
    func=lambda message: Admin.isAdmin(message.chat.id))
def send_message_from_admin(message):
    admin_bot.send_message(message.chat.id, 'Отправь сообщение мне')
    Admin.set_state('send')

@admin_bot.message_handler(content_types=['text'], 
    func=lambda message: Admin.isAdmin(message.chat.id) and Admin.get_state() == 'send')
def answer_send_message_from_admin(message):
    Admin.set_state()
    for user in User.users_list():
        try_send(user, message.text)

@admin_bot.message_handler(commands=['count'],
    func=lambda message: Admin.isAdmin(message.chat.id))
def get_user_count(message):
    admin_bot.send_message(Admin.get_id(), len(User.users_list()))

@admin_bot.message_handler(commands=['feedback'], 
    func=lambda message: Admin.isAdmin(message.chat.id))
def admin_feedback(message):
    pass

@bot.message_handler(commands=['start'])
def start(message):
    try_send(message.chat.id, Template.first_message())

    set_language(chat_id=message.chat.id)

@bot.message_handler(commands=['reset'])
def reset(message):
    try_send(message.chat.id, Template.reset())
    
    set_language(chat_id=message.chat.id)

@bot.message_handler(commands=['about'])
def about(message):
    try_send(message.chat.id, Template.about())

@bot.message_handler(commands=['manual'])
def manual(message):
    try_send(message.chat.id, Template.manual())

@bot.message_handler(commands=['feedback'])
def feed_step_1(message=None, chat_id=None):
    if chat_id == None:
        chat_id = message.chat.id

    user = User(chat_id)
    if user.get_mode() == 'await' or user.check_data() == 'good':
        keyboard = telebot.types.ReplyKeyboardMarkup(
            one_time_keyboard=False,
            resize_keyboard=True
        )
        
        for var in feed_answers:
            keyboard.add(var)

        try_send(chat_id, Template.feed_q(), keyboard)
        user.set_state('feed_1')
    else:
        try_send(chat_id, Template.no_await()) 

@bot.message_handler(content_types=['text'], 
    func=lambda message: User.user_state(message.chat.id) == 'feed_1')
def feed_step_2(message):
    if message.text in feed_answers:
        user = User(message.chat.id)
        user.set_swap('isBad', feed_answers[message.text])
        user.set_state('feed_2')
        try_send(message.chat.id, Template.feed_a(), keyboard_off)
    else:
        try_send(message.chat.id, Template.feed_b_a())

        feed_step_1(chat_id=message.chat.id)

@bot.message_handler(content_types=['text'], 
    func=lambda message: User.user_state(message.chat.id) == 'feed_2')
def feed_step_3(message):
    user = User(message.chat.id)
    user.set_state()
    feedback = FeedbackTemplate(
        message.chat.id,
        user.get_swap()['isBad'],
        message.text
    )
    Feedback.save_feedback(feedback)

@bot.message_handler(commands=['get_words'])
def get_words(message):
    user = User(message.chat.id)
    w = Words(user)
    words = Template.get_words() + '\n'
    for word in w.new_words(10):
        words += '\n' + word
    try_send(message.chat.id, words)

@bot.message_handler(commands=['language'])
def set_language(message=None, chat_id=None, repeat=False):
    if chat_id == None:
        chat_id = message.chat.id
        user = User(chat_id)
    else:
        user = User(chat_id)
        user.set_mode('setting')

    user.set_state('lang')
    keyboard = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )

    for language in languages: 
        keyboard.add(language)
    if not repeat:
        try_send(chat_id, Template.lang_q(), keyboard)

@bot.message_handler(content_types=['text'],
    func=lambda message: User.user_state(message.chat.id) == 'lang')
def answer_set_language(message):
    if message.text in languages:
        user = User(message.chat.id)
        user.set_lang(message.text)

        try_send(message.chat.id, Template.lang_g_a(), keyboard_off)

        user.set_state()
        if user.get_mode() == 'setting':
            set_time(chat_id=message.chat.id)
    else:
        try_send(message.chat.id, Template.lang_b_a())

        set_language(chat_id=message.chat.id, repeat=True)

@bot.message_handler(commands=['time'])
def set_time(message=None, chat_id=None, repeat=False):
    if chat_id == None:
        chat_id = message.chat.id
    
    user = User(chat_id)
    user.set_state('time')

    keyboard = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )

    for t in send_time_var: 
        keyboard.add(t)
    if not repeat:
        try_send(chat_id, Template.time_q(), keyboard)
    
@bot.message_handler(content_types=['text'], 
    func=lambda message: User.user_state(message.chat.id) == 'time')
def answer_set_time(message):
    if message.text in send_time_var:
        user = User(message.chat.id)
        user.set_time(send_time_var[message.text])
        try_send(message.chat.id, Template.time_g_a(), keyboard_off)

        user.set_state()
        if user.get_mode() == 'setting':
            set_count_n(chat_id=message.chat.id)
    else:
        try_send(message.chat.id, Template.time_b_a())

        set_time(chat_id=message.chat.id, repeat=True)
   
@bot.message_handler(commands=['count'])
def set_count_n(message=None, chat_id=None, repeat=False):
    if chat_id == None:
        chat_id = message.chat.id

    user = User(chat_id)
    user.set_state('count_n')

    if not repeat:
        try_send(chat_id, Template.count_n_q())
     
@bot.message_handler(content_types=['text'], 
    func=lambda message: User.user_state(message.chat.id) == 'count_n')
def answer_set_count_n(message):
    if message.text.isdigit():
        count_n = int(message.text)  
        if 5 <= count_n <= 50:
            user = User(message.chat.id)
            user.set_swap('count_n', count_n)
            user.set_state()
            set_count_r(chat_id=message.chat.id)
        else:
            try_send(message.chat.id, Template.limit())
            set_count_n(chat_id=message.chat.id, repeat=True)
    else:
        try_send(message.chat.id, Template.no_digit())
        set_count_n(chat_id=message.chat.id, repeat=True)
        
def set_count_r(chat_id, repeat=False):
    user = User(chat_id)
    user.set_state('count_r')
    if not repeat:
        try_send(chat_id, Template.count_r_q())

@bot.message_handler(content_types=['text'], 
    func=lambda message: User.user_state(message.chat.id) == 'count_r')
def answer_set_count_r(message):
    if message.text.isdigit():
        count_r = int(message.text)
        if 5 <= count_r <= 50:
            user = User(message.chat.id)
            count_n = user.get_swap()['count_n']
            user.set_send_qty(count_n, count_r)
            user.set_state()
            if user.get_mode() == 'setting':
                user.set_mode()
                try_send(message.chat.id, Template.end_set())
        else:
            try_send(message.chat.id, Template.limit())
            set_count_r(chat_id=message.chat.id, repeat=True)
    else:
        try_send(message.chat.id, Template.no_digit())
        set_count_r(chat_id=message.chat.id, repeat=True)


if __name__ == '__main__':
    handler = Thread(target = bot.polling, args=(True,))
    admin = Thread(target=admin_bot.polling, args=(True,))
    send = Thread(target=sender)
    handler.start()
    send.start()
    admin.start()