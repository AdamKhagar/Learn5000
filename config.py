
languages = {'English': 'words/English-words.json'}
send_time_var = {
    'Утром': 1,
    'В обед': 2,
    'Вечером': 3,
    'Ночью': 4
}

profiles = {
    1: ['08:30:00', '10:30:00'],
    2: ['12:30:00', '15:30:00'],
    3: ['17:30:00', '19:00:00'],
    4: ['20:00:00', '23:30:00']
}

feed_answers = {
    'Сообщение об ошибке': True ,
    'Отзыв/предложение': False
}

list_path = 'users_data/users_list.json'
dir_path = 'users_data/user_data#{}'
f_path = {
 'lang': '{}/lang#{}.json',
 'progress': '{}/progess#{}.json',
 'send_qty': '{}/send_qty#{}.json',
 'send_time': '{}/send_time#{}.json',
 'state': '{}/state{}.json',
 'swap': '{}/swap{}.json'
}
