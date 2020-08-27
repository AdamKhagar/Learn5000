import telebot
import json
from datetime import datetime
from config import profiles, languages, send_time_var
from secret import token, admin_token
from time import strftime, sleep
from user import User
from words import Words
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

def get_user_list():
    with open('users_data/users_list.json', encoding='utf-8') as f:
        return json.load(f)

def get_admin_id():
    with open('users_data/admins.json') as f:
        return json.load(f)['id']

def get_admin_state():
    with open('users_data/admins.json') as f:
        return json.load(f)['state']

def set_admin_state(state='await'):
    with open('users_data/admins.json') as f:
        admin_data = json.load(f)
    admin_data['state'] = state
    with open('users_data/admins.json', 'w', encoding='utf-8') as f:
        json.dump(admin_data, f, ensure_ascii=False, indent=4)

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
            if i == 10:
                i = 0
                sleep(1)
            user.set_last_day()
            if user.check_data() == 'data error':
                # data error
                i += 1
                print('problem_data')
                print(u)
                with open('templates/data-error.txt', encoding='utf-8') as f:
                    try_send(u, f.read())

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
                print('хрень')

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
    last_time = 0
    while True:  
        if last_time != time_zone() and time_zone() != False: 
            last_time = time_zone()
            send_messages(get_user_list())
        else:
            sleep(10*60)

def get_current_state(user_id):
    user = User(user_id)
    return user.get_state()

@admin_bot.message_handler(commands=['send'],
    func=lambda message: message.chat.id == get_admin_id())
def send_message_from_admin(message):
    admin_bot.send_message(message.chat.id, 'Отправь сообщение мне')
    set_admin_state('send')

@admin_bot.message_handler(content_types=['text'], 
    func=lambda message: message.chat.id == get_admin_id() and get_admin_state() == 'send')
def answer_send_message_from_admin(message):
    set_admin_state()
    for user in get_user_list():
        try_send(user, message.text)

@bot.message_handler(commands=['start'])
def start(message):
    with open('temlates/first_message.txt', encoding='utf-8') as f:
        try_send(message.chat.id, f.read())

    set_language(chat_id=message.chat.id)

@bot.message_handler(commands=['reset'])
def reset(message):
    with open('templates/first_message.txt', encoding='utf-8') as f:
        try_send(message.chat.id, f.read())
    
    set_language(chat_id=message.chat.id)

@bot.message_handler(commands=['about'])
def about(message):
    with open('about.txt', encoding='utf-8') as f:
        try_send(message.chat.id, f.read())

@bot.message_handler(commands=['feedback'])
def feedback(message):
    with open('feedback.txt', encoding='utf-8') as f:
        try_send(message.chat.id, f.read())

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
        with open('templates/lang_q.txt', encoding='utf-8') as f:
            try_send(chat_id, f.read(), keyboard)

@bot.message_handler(content_types=['text'],
    func=lambda message: get_current_state(message.chat.id) == 'lang')
def answer_set_language(message):
    if message.text in languages:
        user = User(message.chat.id)
        user.set_lang(message.text)

        with open('templates/lang_g_a.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read(), keyboard_off)

        user.set_state()
        if user.get_mode() == 'setting':
            set_time(chat_id=message.chat.id)
    else:
        with open('templates/lang_b_a.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read())

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
        with open('templates/time_q.txt', encoding='utf-8') as f:
            try_send(chat_id, f.read(), keyboard)
    
@bot.message_handler(content_types=['text'], 
    func=lambda message: get_current_state(message.chat.id) == 'time')
def answer_set_time(message):
    if message.text in send_time_var:
        user = User(message.chat.id)
        user.set_time(send_time_var[message.text])
        with open('templates/time_g_a.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read(), keyboard_off)

        user.set_state()
        if user.get_mode() == 'setting':
            set_count_n(chat_id=message.chat.id)
    else:
        with open('templates/time_b_a.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read())

        set_time(chat_id=message.chat.id, repeat=True)
   
@bot.message_handler(commands=['count'])
def set_count_n(message=None, chat_id=None, repeat=False):
    if chat_id == None:
        chat_id = message.chat.id

    user = User(chat_id)
    user.set_state('count_n')

    if not repeat:
        with open('templates/count_n_q.txt', encoding='utf-8') as f:
            try_send(chat_id, f.read())

@bot.message_handler(content_types=['text'], 
    func=lambda message: get_current_state(message.chat.id) == 'count_n')
def answer_set_count_n(message):
    if message.text.isdigit():
        count_n = int(message.text)

        user = User(message.chat.id)
        user.set_swap({'count_n': count_n})
        user.set_state()

        set_count_r(chat_id=message.chat.id)
    else:
        with open('templates/no_digit.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read())

        set_count_n(chat_id=message.chat.id)
        
def set_count_r(chat_id, repeat=False):

    user = User(chat_id)
    user.set_state('count_r')
    if not repeat:
        with open('templates/count_r_q.txt', encoding='utf-8') as f:
            try_send(chat_id, f.read())

@bot.message_handler(content_types=['text'], 
    func=lambda message: get_current_state(message.chat.id) == 'count_r')
def answer_set_count_r(message):
    if message.text.isdigit():
        count_r = int(message.text)
        user = User(message.chat.id)
        count_n = user.get_swap()['count_n']
        user.set_send_qty(count_n, count_r)
        user.set_state()
        if user.get_mode() == 'setting':
            user.set_mode()
            with open('templates/end_set.txt', encoding='utf-8') as f:
                try_send(message.chat.id, f.read())
    else:
        with open('templates/no_digit.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read())

        set_count_r(chat_id=message.chat.id, repeat=True)


if __name__ == '__main__':
    handler = Thread(target = bot.polling)
    admin = Thread(target=admin_bot.polling)
    send = Thread(target=sender)
    handler.start()
    send.start()
    admin.start()