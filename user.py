import json
import os
from time import strftime
from shutil import rmtree
from config import languages

class User():
    ''' It's a simple dbms '''
    def __init__(self, user_id):
        self.__id = user_id
        self.__path_dir = f'users_data/user_data#{self.__id}'
        self.__users_f = 'users_data/users_list.json'
        self.__swap_f = f'{self.__path_dir}/swap#{self.__id}.json'
        self.__state_f = f'{self.__path_dir}/state#{self.__id}.json'
        self.__progress_f = f'{self.__path_dir}/progress#{self.__id}.json'
        self.__lang_f = f'{self.__path_dir}/lang#{self.__id}.json'
        self.__send_time_f = f'{self.__path_dir}/send_time#{self.__id}.json'
        self.__qty_f = f'{self.__path_dir}/send_qty#{self.__id}.json'
        self.__history_f = f'{self.__path_dir}/history#{self.__id}.json'
        self.__mode_f = f'{self.__path_dir}/mode#{self.__id}.json'
        try: 
            os.mkdir(self.__path_dir)
        except OSError:
            pass
        finally:
            self.__new()                 

    def __new(self):
        '''this func adds the user to the user_list.json if he is not exist'''
        users = self.__get(self.__users_f)
        if self.__id not in users:
            users.append(self.__id)
            self.__set(users, self.__users_f)
            self.set_state()

    def __set(self, data, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def __get(self, path: 'file path'):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def set_mode(self, mode='await'):
        self.__set(mode, self.__mode_f)

    def get_mode(self):
        try:
            return self.__get(self.__mode_f)
        except FileNotFoundError:
            self.set_mode()
            return 'await'

    def set_swap(self, key, value):
        '''save on the clipboard'''
        try:
            swap = self.get_swap()
        except FileNotFoundError:
            swap = {}
        finally:
            swap[key] = value
            self.__set(swap, self.__swap_f)

    def get_swap(self):
        '''get it from the clipboard''' 
        return self.__get(self.__swap_f)
        
    def set_state(self, state='await'):
        '''set user state'''
        self.__set(state, self.__state_f)

    def get_state(self):
        '''get user state'''
        try:
            return self.__get(self.__state_f)
        except FileNotFoundError:
            self.set_state()
        else:
            self.get_state()
        
    def set_lang(self, lang):
        '''select current language'''
        self.__set(lang, self.__lang_f)

    def get_lang(self):
        '''get current language'''
        try:
            return self.__get(self.__lang_f)
        except FileNotFoundError:
            return False
        
    def set_time(self, send_time):
        '''set the time of shipment'''
        self.__set(send_time, self.__send_time_f)

    def get_time(self):
        '''get shipping time'''
        try:
            return self.__get(self.__send_time_f)
        except FileNotFoundError:
            return False

    def set_send_qty(self, qty_n, qty_r):
        '''set word count per day'''
        setting = (qty_n, qty_r)
        self.__set(setting, self.__qty_f)

    def get_send_qty(self):
        '''get word count per day'''
        try:
            return self.__get(self.__qty_f)
        except FileNotFoundError:
            return False

    def set_last_day(self):
        '''mark the last shipment'''
        self.__set(strftime('%x'), self.__history_f)

    def get_last_day(self):
        '''get last shipment'''
        try: 
            h = self.__get(self.__history_f)
        except FileNotFoundError:
            return False
        else: 
            return h

    def get_progress(self, lang):
        try:
            used = self.__get(self.__progress_f)
        except FileNotFoundError:
            used = {}
            for l in languages:
                used[l] = []
        finally:
            return used[lang]

    def set_progress(self, lang, progress):
        try:
            used = self.__get(self.__progress_f)
        except FileNotFoundError: 
            used = {}
        finally:
            used[lang] = progress
            self.__set(used, self.__progress_f)

    def check_data(self):
        if not self.get_lang() or not self.get_time() or not self.get_send_qty():
            return 'data error'
        elif self.get_state() != 'await':
            return 'no await'
        else:
            return 'good'
        
    def del_user(self):
        try:
            rmtree(self.__path_dir)
        except FileExistsError:
            pass
        users = self.__get(self.__users_f)
        users.remove(self.__id)
        self.__set(users, self.__users_f)
        
    @staticmethod
    def users_list():
        with open('users_data/users_list.json', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def user_state(user_id):
        user = User(user_id)
        return user.get_state()