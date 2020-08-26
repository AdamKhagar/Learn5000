import telebot
import json
from datetime import datetime
from config import profiles, languages, send_time_var
from secret import token
from time import strftime, sleep
from user import User
from words import Words
from threading import Thread


bot = telebot.TeleBot(token)
keyboard_off = telebot.types.ReplyKeyboardRemove()

def try_send(user_id, text, keyboard=None):
    '''does the same telebot.send_message() and deletes data from locked chats'''
    try:
        bot.send_message(user_id, text, reply_markup=keyboard)
    # обработка заблокированных чатов
    except telebot.apihelper.ApiException:
        user = User(user_id)
        print(f'delete user#{user_id}')
        user.del_user()

def get_user_list():
    with open('users_data/users_list.json', encoding='utf-8') as f:
        return json.load(f)

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
            if user.check_data() == 1:
                # data error
                i += 1
                print('problem_data')
                print(u)
                with open('templates/data-error.txt', encoding='utf-8') as f:
                    try_send(u, f.read())

            elif user.check_data() == 2:
                # no message waiting
                print('no message waiting')
                print(u)

            elif user.check_data():
                # all rigtht
                i += 1
                w = Words(user)
                words = w.get_words()
                print('ok')

                try_send(u, words)

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

# def sleep_time():
#     '''это функция расчитывает время сна для потока send'''
#     '''это нужно что бы поток зас
#     current = time_zone()
#     if current == 4:
#         next_t = profiles[1][0]

#     else:
#         next_t = profiles[1 + current][0]

def sender():
    while True: 
        if time_zone() == False:
            print('check_time')
            sleep(30*60)
        else: 
            print('\n\n\n')
            send_messages(get_user_list())


def get_current_state(user_id):
    user = User(user_id)
    return user.get_state()

@bot.message_handler(commands=['start'])
def start(message):
    with open('temlates/first_message.txt', encoding='utf-8') as f:
        try_send(message.chat.id, f.read())

    setting_1(chat_id = message.chat.id)

@bot.message_handler(commands=['reset'])
def setting_1(message = None, chat_id = None):
    if message != None:
        chat_id = message.chat.id
        with open('templates/reset.txt', encoding='utf-8') as f:
            try_send(chat_id, f.read())

    user = User(chat_id)
    user.set_state('set_lang')

    keyboard = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )

    for language in languages: 
        keyboard.add(language)

    with open('templates/lang_q.txt', encoding='utf-8') as f:
        try_send(chat_id, f.read(), keyboard)

@bot.message_handler(content_types=['text'],
    func=lambda message: get_current_state(message.chat.id) == 'set_lang')
def answer_setting_1(message):
    if message.text in languages:
        user = User(message.chat.id)
        user.set_lang(message.text)

        with open('templates/lang_q_a.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read(), keyboard_off)

        setting_2(message.chat.id)
    else:
        with open('templates/repeat.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read())

        choise_language(chat_id=message.chat.id)

def setting_2(chat_id):
    user = User(chat_id)
    user.set_state('set_time')

    keyboard = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )

    for t in send_time_var: 
        keyboard.add(t)

    with open('templates/time_q.txt', encoding='utf-8') as f:
        try_send(chat_id, f.read(), keyboard)

@bot.message_handler(content_types=['text'],
    func=lambda message: get_current_state(message.chat.id) == 'set_time')
def answer_setting_2(message):
    if message.text in send_time_var:
        user = User(message.chat.id)
        user.set_time(send_time_var[message.text])

        with open('templates/time_g_a.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read(), keyboard_off)

        setting_3(message.chat.id)
    else:
        with open('templates/time_b_a.txt', encoding='utf-8') as f:
            try_send(message.chat.id, f.read())

        set_time(chat_id=message.chat.id)

def setting_3(chat_id):
    user = User(chat_id)
    user.set_state('set_count_n')

    bot.send_message(
        chat_id,
        'Сколько новых слов в день осилишь?'
    )

@bot.message_handler(content_types=['text'],
    func=lambda message: get_current_state(message.chat.id) == 'set_count_n')
def answer_setting_3(message):
    if message.text.isdigit():
        count_n = int(message.text)
        max_count = 30
        if count_n <= max_count:
            user = User(message.chat.id)
            user.set_swap({'count_n': count_n})
            user.set_state('set_count_r')

            bot.send_message(
                message.chat.id,
                'Сколько слов для повторения добавить?'
            )
        else: 
            bot.send_message(
                message.chat.id, 
                f'ВОУ сбавь обороты. Максимум слов в день {max_count}'
            )
    else:
        bot.send_message(
            message.chat.id,
            'Я кушаю только целые числа. Давай по-новой'
        )

        setting_3(chat_id=message.chat.id)


@bot.message_handler(content_types=['text'],
    func=lambda message: get_current_state(message.chat.id) == 'set_count_r')
def answer_setting_4(message):
    if message.text.isdigit():
        count_r = int(message.text)

        user = User(message.chat.id)
        count_n = user.get_swap()['count_n']
        user.set_send_qty(count_n, count_r)
        user.set_state()

        bot.send_message(
            message.chat.id,
            'Настройка завершена'
        )    
    else:
        bot.send_message(
            message.chat.id,
            'Я кушаю только целые числа. Давай по-новой'
        )
        set_count_r(chat_id=message.chat.id)

@bot.message_handler(commands=['about'])
def about(message):
    with open('about.txt', 'r', encoding='utf-8') as f:
        bot.send_message(
            message.chat.id,
            f.read()
        )

@bot.message_handler(commands=['feedback'])
def feedback(message):
    bot.send_message(
        message.chat.id,
        'Функция фидбека еще не работает так что жрите мои баги)'
    )

@bot.message_handler(commands=['language'])
def choise_language(message=None, chat_id=None):
    if chat_id == None:
        chat_id = message.chat.id

    user = User(chat_id)
    user.set_state('lang')

    keyboard = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )

    for language in languages: 
        keyboard.add(language)

    bot.send_message(
        chat_id,
        'Какой язык учим?',
        reply_markup=keyboard
    )

@bot.message_handler(content_types=['text'],
    func=lambda message: get_current_state(message.chat.id) == 'lang')
def answer_choise_language(message):
    if message.text in languages:
        user = User(message.chat.id)
        user.set_lang(message.text)

        bot.send_message(
            message.chat.id,
            'Хорошо'
        )

        user.set_state()
    else:
        bot.send_message(
            message.chat.id,
            'Повторика еще раз',
            reply_markup=keyboard_off
        )

        choise_language(chat_id=message.chat.id)

@bot.message_handler(commands=['time'])
def set_time(message=None, chat_id = None):
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

    bot.send_message(chat_id,
        'В какое время тебе удобно учить слова?',
        reply_markup=keyboard
    )
    
@bot.message_handler(content_types=['text'], 
    func=lambda message: get_current_state(message.chat.id) == 'time')
def answer_set_time(message):
    if message.text in send_time_var:
        user = User(message.chat.id)
        user.set_time(send_time_var[message.text])
        bot.send_message(
            message.chat.id,
            'Принято',
            reply_markup=keyboard_off
        )
        user.set_state()
    else:
        bot.send_message(
            message.chat.id,
            'Ну ка повтори'
        )
        set_time(chat_id=message.chat.id)

   
@bot.message_handler(commands=['count'])
def set_count_n(message=None, chat_id=None):
    if chat_id == None:
        chat_id = message.chat.id

    user = User(chat_id)
    user.set_state('count_n')

    bot.send_message(
        chat_id,
        'Сколько новых слов в день осилишь?'
    )

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
        bot.send_message(
            message.chat.id,
            'Я кушаю только целые числа. Давай по-новой'
        )

        set_count_n(chat_id=message.chat.id)
        
def set_count_r(message=None, chat_id=None):
    if chat_id == None:
        chat_id = message.chat.id

    user = User(chat_id)
    user.set_state('count_r')

    bot.send_message(
        chat_id,
        'Сколько слов для повторения добавить?'
    )

@bot.message_handler(content_types=['text'], 
    func=lambda message: get_current_state(message.chat.id) == 'count_r')
def answer_set_count_r(message):
    if message.text.isdigit():
        count_r = int(message.text)
        user = User(message.chat.id)
        count_n = user.get_swap()['count_n']
        user.set_send_qty(count_n, count_r)
        user.set_state()
    else:
        bot.send_message(
            message.chat.id,
            'Я кушаю только целые числа. Давай по-новой'
        )
        set_count_r(chat_id=message.chat.id)

if __name__ == '__main__':
    handler = Thread(target = bot.polling(none_stop= False))
    send = Thread(target=sender)
    try:
        handler.start()
        send.start()
    except KeyboardInterrupt:
        quit()
    
