import json
import telebot

class Admin:
    feedback_var = {'Только сообщения об ошибках': True, 'Все отзывы': False}
    feedback_options = {'Ответить': 1, 'Пропустить': 2, 'Закрыть': 3}
    feedback_options_after_reply = {'Дальше': 2, 'Закрыть': 3}

    @staticmethod
    def isAdmin(user_id):
        with open('users_data/admins.json', encoding='utf-8') as f:
            admin_data = json.load(f)
        
        return admin_data['id'] == user_id

    @staticmethod
    def get_id():
        with open('users_data/admins.json', encoding='utf-8') as f:
            return json.load(f)['id']     
            
    @staticmethod
    def get_state():
        with open('users_data/admins.json', encoding='utf-8') as f:
            return json.load(f)['state']

    @staticmethod
    def set_state(state='await'):
        with open('users_data/admins.json', encoding='utf-8') as f:
            admin_data = json.load(f)
        admin_data['state'] = state
        with open('users_data/admins.json', 'w', encoding='utf-8') as f:
            json.dump(admin_data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def get_current_feed():
        with open('users_data/admins.json', encoding='utf-8') as f:
            return json.load(f)['current_feed']

    @staticmethod
    def set_current_feed(current_feed):
        with open('users_data/admins.json', encoding='utf-8') as f:
            admin_data = json.load(f)
        admin_data['current_feed'] = current_feed
        with open('users_data/admins.json', 'w', encoding='utf-8') as f:
            json.dump(admin_data, f, ensure_ascii=False, indent=4)
        

    @staticmethod
    def get_isBad():
        with open('users_data/admins.json', encoding='utf-8') as f:
            return json.load(f)['isBad']

    @staticmethod
    def set_isBad(isBad: bool):
        with open('users_data/admins.json', encoding='utf-8') as f:
            admin_data = json.load(f)
        admin_data['isBad'] = isBad
        with open('users_data/admins.json', 'w', encoding='utf-8') as f:
            json.dump(admin_data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def feed_keyboard():
        keyboard = telebot.types.ReplyKeyboardMarkup(
            one_time_keyboard=False,
            resize_keyboard=True
        )
        for option in Admin.feedback_options:
            keyboard.add(option)
        return keyboard

    @staticmethod
    def feed_keyboard_after_reply():
        keyboard = telebot.types.ReplyKeyboardMarkup(
            one_time_keyboard=False,
            resize_keyboard=True
        )
        for option in Admin.feedback_options_after_reply:
            keyboard.add(option)
        return keyboard