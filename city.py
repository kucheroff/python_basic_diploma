import telebot
from telebot import types
from req import req
import re
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


class City:
    def __init__(self):
        self.city_list = []
        self.destination_id = None

    def get_city(self, message):
        city_name = message.text
        data = req("https://hotels4.p.rapidapi.com/locations/search", {"query": city_name, "locale": "ru_RU"})
        if data:
            data = data['suggestions'][0]['entities']
            city_data = map(lambda elem: {'destId': elem['destinationId'], 'name': elem['name'], 'type': elem['type'],
                                          'capt': re.sub(r'<.*?>', '', elem['caption'])}, data)
            city_data = filter(lambda elem: elem['type'] == 'CITY', city_data)
            self.city_list = list(city_data)
            if len(self.city_list) > 0:
                print('Список возможных локаций:')
                choice = 1
                keyboard = types.InlineKeyboardMarkup()

                for city in self.city_list:
                    keyboard.add(types.InlineKeyboardButton(text=f'{choice}: {city["capt"]}', callback_data=choice))
                    print(f'{choice}: {city["capt"]}')
                    choice += 1

                bot.send_message(message.chat.id, text='Список возможных локаций:', reply_markup=keyboard)
            else:
                print('Локация не найдена')
                bot.send_message(message.from_user.id, 'Локация не найдена. Попробуйте другую.')
        else:
            bot.send_message(message.from_user.id, 'Нет связи с сервером')

    def get_destination_id(self, idx):
        self.destination_id = self.city_list[int(idx) - 1]['destId']


