import re
import datetime
from req import req
import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


class Hotel:
    loc_dict = {'ru_RU': ['Рейтинг:', 'Цена:', 'От центра города', 'Адрес:'],
                'en_US': ['Rating:', 'Price:', 'From city center', 'Адрес:']}

    def __init__(self):
        self.sort_order = None
        self.min_price = str
        self.max_price = str
        self.max_distance = 0
        self.p_size = 0
        self.currency = None
        self.__loc = None

    def get_hotel(self, dest_id, srt_mode, ch_id):
        date_in = str(datetime.datetime.today().date())
        date_out = str(datetime.datetime.today().date() + datetime.timedelta(days=1))

        querystring = {"adults1": "1",
                       "pageNumber": "1",
                       "destinationId": dest_id,
                       "checkOut": date_out,
                       "checkIn": date_in,
                       "sortOrder": srt_mode,
                       "locale": self.__loc,
                       "landmarkIds": "City center",
                       "currency": self.currency}

        if self.sort_order == 'DISTANCE_FROM_LANDMARK':
            querystring["priceMax"] = self.max_price
            querystring["priceMin"] = self.min_price


        querystring["pageSize"] = self.p_size
        hotel_data = req("https://hotels4.p.rapidapi.com/properties/list", querystring)
        if hotel_data['result'] == 'OK':
            result_list = hotel_data['data']['body']['searchResults']['results']
            print(result_list)
            if len(result_list) != 0:
                hotel_list = [{
                    'name': i_dict['name'],
                    'rating': i_dict.get('guestReviews', {}).get('rating', '--'),
                    'address': i_dict.get('address', {}).get('streetAddress', ''),
                    'location': i_dict.get('address', {}).get('locality', ''),
                    'country': i_dict.get('address', {}).get('countryName', ''),
                    'price': i_dict.get('ratePlan', {}).get('price', '').get('current', '--'),
                    'center_distance': i_dict.get('landmarks', '')[0].get('distance', '--'),
                    'stars': i_dict.get('starRating', '--')} for i_dict in result_list]

                print(hotel_list)

                if srt_mode == 'DISTANCE_FROM_LANDMARK':
                    hotel_list = [i_dict for i_dict in hotel_list
                                  if float(re.sub(',', '.', re.match(r'[0-9,]+', i_dict['center_distance']).group())) <=
                                  float(self.max_distance)]
                    hotel_list = sorted(hotel_list, key=lambda dct: int(re.sub('[^0-9]+', '', dct['price'])))
                    if len(hotel_list) == 0:
                        bot.send_message(ch_id, 'Нет отелей по заданным параметрам.')

                for i_dict in hotel_list:
                    if isinstance(i_dict["stars"], float):
                        stars = '\U00002B50' * int(i_dict["stars"])
                    else:
                        stars = '--'
                    text = f'<strong>{i_dict["name"]}.</strong>\n' \
                           f'{stars} {self.loc_dict[self.__loc][0]} {i_dict["rating"]}.' \
                           f' {self.loc_dict[self.__loc][1]} <b>{i_dict["price"]}</b>.\n' \
                           f'{self.loc_dict[self.__loc][2]} <b>{i_dict["center_distance"]}</b>.\n' \
                           f'{self.loc_dict[self.__loc][3]} {i_dict["address"]}, {i_dict["location"]}.'
                    bot.send_message(ch_id, text, parse_mode='HTML')
            else:
                bot.send_message(ch_id, 'Нет отелей по заданным параметрам.')
        else:
            print('Нет данных о данной локации')

    def set_loc(self, loc):
        self.__loc = loc