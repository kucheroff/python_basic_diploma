import telebot
from telebot import types
from req import req
import re
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


class City:
    def __init__(self):
        self.__city_list = []
        self.__destination_id = None
        self.__loc = None

    def get_city(self, message):
        city_name = message.text
        pattern = r'[A-Z,a-z]*'
        self.__loc = 'en_US' if re.match(pattern, city_name).group() else 'ru_RU'
        data = req("https://hotels4.p.rapidapi.com/locations/search", {"query": city_name, "locale": self.__loc})
        if data:
            data = data['suggestions'][0]['entities']
            city_data = map(lambda elem: {'destId': elem['destinationId'], 'name': elem['name'], 'type': elem['type'],
                                          'capt': re.sub(r'<.*?>', '', elem['caption'])}, data)
            city_data = filter(lambda elem: elem['type'] == 'CITY', city_data)
            self.__city_list = list(city_data)
            if len(self.__city_list) > 0:
                print('Список возможных локаций:')
                choice = 1
                keyboard = types.InlineKeyboardMarkup()

                for city in self.__city_list:
                    keyboard.add(types.InlineKeyboardButton(text=f'{choice}: {city["capt"]}', callback_data=choice))
                    print(f'{choice}: {city["capt"]}')
                    choice += 1

                bot.send_message(message.chat.id, text='Список возможных локаций:', reply_markup=keyboard)
            else:
                print('Локация не найдена')
                bot.send_message(message.from_user.id, 'Локация не найдена. Попробуйте другую.')
        else:
            bot.send_message(message.from_user.id, 'Нет связи с сервером')

    def get_loc(self):
        return self.__loc

    def set_loc(self, loc):
        self.__loc = loc

    def get_destination_id(self):
        return self.__destination_id

    def set_destination_id(self, idx):
        self.__destination_id = self.__city_list[int(idx) - 1]['destId']

    def get_city_list(self):
        return self.__city_list



