#  parser for https://studynow.ru/dicta/allwords
################################################

import requests
from bs4 import BeautifulSoup
import json

URL = 'https://studynow.ru/dicta/allwords'

responce = requests.get(URL)
soup = BeautifulSoup(responce.text, 'html.parser')
columns = soup.findAll('tr')

word_dict = []

for column in columns: 
    string = '{} - {}'
    column = column.findAll('td')
    string = string.format(column[1].get_text(), column[2].get_text())

    word_dict.append(string)

with open("words/words.json", "w", encoding="utf-8") as words:
    json.dump(word_dict, words, ensure_ascii=False, indent=4)