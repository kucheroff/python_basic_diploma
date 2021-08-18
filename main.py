import telebot
import re
from telebot import types
from city import City
from hotel import Hotel
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

city = City()
hotel = Hotel()


@bot.message_handler(commands=["start"])
def start(message):
    low_command = types.KeyboardButton('/lowprice')
    high_command = types.KeyboardButton('/highprice')
    best_command = types.KeyboardButton('/bestdeal')
    kbd = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kbd.row(low_command, high_command, best_command)
    bot.send_message(message.from_user.id, "Поиск отелей.", reply_markup=kbd)


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def commands(message):
    if message.text == "/lowprice":
        hotel.sort_order = 'PRICE'
        bot.send_message(message.from_user.id, "Поиск от дешевых к дорогим.\nКакой город искать?")
    elif message.text == "/highprice":
        hotel.sort_order = 'PRICE_HIGHEST_FIRST'
        bot.send_message(message.from_user.id, "Поиск от дорогих к дешевым.\nКакой город искать?")
    elif message.text == "/bestdeal":
        hotel.sort_order = 'DISTANCE_FROM_LANDMARK'
        bot.send_message(message.from_user.id, "Поиск Лучших предложений.\nКакой город искать?")
    bot.register_next_step_handler(message, city.get_city)


@bot.message_handler(commands=["help"])
def help_message(message):
    bot.send_message(message.from_user.id, "/lowprice: поиск от дешевых к дорогим.\n"
                                           "/highprice: поиск от дорогих к дешевым.\n"
                                           "/bestdeal: поиск Лучших предложений.")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data.isdigit():
        city.get_destination_id(call.data)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, f'Ищем в {city.city_list[int(call.data)-1]["capt"]}')
        cur_1 = types.InlineKeyboardButton(text='RUB', callback_data='RUB')
        cur_2 = types.InlineKeyboardButton(text='EURO', callback_data='EUR')
        cur_3 = types.InlineKeyboardButton(text='USD', callback_data='USD')
        keyboard = types.InlineKeyboardMarkup().row(cur_1, cur_2, cur_3)

        bot.send_message(call.message.chat.id, text='Валюта:', reply_markup=keyboard)
    else:
        hotel.currency = call.data
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, 'Сколько результатов выводить?')
        bot.register_next_step_handler(call.message, set_page)


def set_page(message):
    if not is_correct(message.text, 1, 'int'):
        bot.send_message(message.chat.id, 'Введите одно положительное число')
        bot.register_next_step_handler(message, set_page)
        return
    hotel.p_size = message.text
    if hotel.sort_order == 'DISTANCE_FROM_LANDMARK':
        bot.send_message(message.chat.id, 'Диапазон цен через пробел:')
        bot.register_next_step_handler(message, set_price)
    else:
        hotel.get_price(city.destination_id, hotel.sort_order, message.chat.id)


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
    mn, mx = m_text.split()
    mn, mx = min(mn, mx), max(mn, mx)
    hotel.min_price, hotel.max_price = mn, mx
    bot.send_message(message.chat.id, 'Максимальное расстояние до центра города:')
    bot.register_next_step_handler(message, set_distance)


def set_distance(message):
    m_text = is_correct(message.text, 1, 'float')
    if not m_text:
        bot.send_message(message.chat.id, 'Введите одно число:')
        bot.register_next_step_handler(message, set_distance)
        return
    hotel.max_distance = float(m_text)
    hotel.get_price(city.destination_id, hotel.sort_order, message.chat.id)


def is_correct(str_num: str, count: int, n_type: str):
    if len(str_num.split()) != count:
        return None
    str_num = re.sub(r',', '.', str_num)
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


bot.polling(none_stop=True, interval=0)


