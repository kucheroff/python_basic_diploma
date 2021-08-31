import os
import telebot
import re
from telebot import types
from city import City
from hotel import Hotel
from user import User

# from config import TOKEN
from decouple import config

TOKEN_API = config('TOKEN')
bot = telebot.TeleBot(TOKEN_API)

# city = City()
# hotel = Hotel()
users = dict()


@bot.message_handler(commands=["start"])
def start(message):
    # users[message.chat.id] = User(message.chat.id, 0)
    low_command = types.KeyboardButton('/lowprice')
    high_command = types.KeyboardButton('/highprice')
    best_command = types.KeyboardButton('/bestdeal')
    kbd = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kbd.row(low_command, high_command, best_command)
    bot.send_message(message.from_user.id, "Поиск отелей.", reply_markup=kbd)


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def commands(message):
    users[message.chat.id] = User(message.chat.id, 1)

    if message.text == "/lowprice":
        users[message.chat.id].hotel.sort_order = 'PRICE'
        bot.send_message(message.from_user.id, "Поиск от дешевых к дорогим.\nКакой город искать?")
    elif message.text == "/highprice":
        users[message.chat.id].hotel.sort_order = 'PRICE_HIGHEST_FIRST'
        bot.send_message(message.from_user.id, "Поиск от дорогих к дешевым.\nКакой город искать?")
    elif message.text == "/bestdeal":
        users[message.chat.id].hotel.sort_order = 'DISTANCE_FROM_LANDMARK'
        bot.send_message(message.from_user.id, "Поиск Лучших предложений.\nКакой город искать?")

    file = open('cid_file.save', 'w')
    for i_key in users.keys():
        file.write(str(i_key) + '\n')
    file.close()

    bot.register_next_step_handler(message, users[message.chat.id].city.get_city)


@bot.message_handler(commands=["help"])
def help_message(message):
    bot.send_message(message.from_user.id, "/lowprice: поиск от дешевых к дорогим.\n"
                                           "/highprice: поиск от дорогих к дешевым.\n"
                                           "/bestdeal: поиск Лучших предложений.")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data.isdigit():
        users[call.message.chat.id].city.set_destination_id(call.data)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, f'Ищем в {users[call.message.chat.id].city.get_city_list()[int(call.data) - 1]["capt"]}')
        cur_1 = types.InlineKeyboardButton(text='RUB', callback_data='RUB')
        cur_2 = types.InlineKeyboardButton(text='EURO', callback_data='EUR')
        cur_3 = types.InlineKeyboardButton(text='USD', callback_data='USD')
        keyboard = types.InlineKeyboardMarkup().row(cur_1, cur_2, cur_3)

        bot.send_message(call.message.chat.id, text='Валюта:', reply_markup=keyboard)
    else:
        users[call.message.chat.id].hotel.currency = call.data
        users[call.message.chat.id].hotel.set_loc(users[call.message.chat.id].city.get_loc())
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, 'Сколько результатов выводить?')
        bot.register_next_step_handler(call.message, set_page)


def set_page(message):
    if not is_correct(message.text, 1, 'int'):
        bot.send_message(message.chat.id, 'Введите одно положительное число')
        bot.register_next_step_handler(message, set_page)
        return
    users[message.chat.id].hotel.p_size = message.text
    if users[message.chat.id].hotel.sort_order == 'DISTANCE_FROM_LANDMARK':
        bot.send_message(message.chat.id, f'Диапазон цен в {users[message.chat.id].hotel.currency} через пробел:')
        bot.register_next_step_handler(message, set_price)
    else:
        users[message.chat.id].hotel.get_hotel(users[message.chat.id].city.get_destination_id(), users[message.chat.id].hotel.sort_order, message.chat.id)
        users.pop(message.chat.id)
        bot.send_message(message.chat.id, f'Спасибо за использование нашего сервиса.')

def set_currency(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='RUB', callback_data='RUB'))
    keyboard.add(types.InlineKeyboardButton(text='EURO', callback_data='EURO'))
    keyboard.add(types.InlineKeyboardButton(text='USD', callback_data='USD'))
    bot.send_message(message.chat.id, text='Валюта:', reply_markup=keyboard)


def set_price(message):
    m_text = is_correct(message.text, 2, 'int')
    if not m_text:
        bot.send_message(message.chat.id, 'Два целых числа через пробел:')
        bot.register_next_step_handler(message, set_price)
        return
    num_1, num_2 = m_text.split()
    mn, mx = min(int(num_1), int(num_2)), max(int(num_1), int(num_2))
    users[message.chat.id].hotel.min_price, users[message.chat.id].hotel.max_price = mn, mx
    bot.send_message(message.chat.id, 'Максимальное расстояние до центра города:')
    bot.register_next_step_handler(message, set_distance)


def set_distance(message):
    m_text = is_correct(message.text, 1, 'float')
    if not m_text:
        bot.send_message(message.chat.id, 'Введите одно число:')
        bot.register_next_step_handler(message, set_distance)
        return
    users[message.chat.id].hotel.max_distance = float(m_text)
    users[message.chat.id].hotel.get_hotel(users[message.chat.id].city.get_destination_id(), users[message.chat.id].hotel.sort_order, message.chat.id)
    users[message.chat.id].step = 2
    bot.send_message(message.chat.id, f'Спасибо за использование нашего сервиса.')


def is_correct(str_num: str, count: int, n_type: str):
    if len(str_num.split()) != count:
        return None
    str_num = re.sub(r',', '..', str_num)
    if n_type == 'int':
        try:
            for i_num in str_num.split():
                if int(i_num) < 0:
                    return None
        except ValueError:
            return None
        return str_num

    if n_type == 'float':
        try:
            for i_num in str_num.split():
                if float(i_num) < 0:
                    return None
        except ValueError:
            return None
        return str_num


if os.path.exists('cid_file.save'):
    f = open('cid_file.save', 'r')
    for i_line in f:
        bot.send_message(int(i_line), f'Произошел сбой в работе сервера.\nПросьба выбрать команду заново.')
    f.close()
    os.remove('cid_file.save')

bot.polling(none_stop=True, interval=0)


