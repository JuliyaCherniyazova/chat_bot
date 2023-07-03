from datetime import datetime

import vk_api

from config import acces_token


class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)

    # Получаем информацию о пользователе
    def get_profile_info(self, user_id):
        info, = self.api.method(
            'users.get',
            {
                'user_id': user_id,
                'fields': 'city, bdate, sex, relation'
            }
        )

        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'sex': info['sex'],
                     'city': info['city']['id'] if 'city' in info else None,
                     }
        return user_info

    # Ищем пользователей подходящих нашему "клиенту"
    def serch_users(self, params, offset=0):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method(
            'users.search',
            {
                'count': 50,
                'offset': offset,
                'age_from': age_from,
                'age_to': age_to,
                'sex': sex,
                'city': city,
                'status': 6,
                'is_closed': False
            }
        )

        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            })

        print(res)
        return res

    # Берем фотографии по id пользователя из анкеты
    def get_photos(self, user_id):
        photos = self.api.method(
            'photos.get',
            {
                'user_id': user_id,
                'album_id': 'profile',
                'extended': 1
            }
        )

        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []
        user_photos = ''
        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        })

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)

        for photo in res[:3]:
            user_photos += f'photo{photo["owner_id"]}_{photo["id"]},'

        print(user_photos)
        return user_photos

    # Получаем id города по запросу бота (запускаем если у пользователя не указан город)
    def get_city_id(self, city_name):
        cities = self.api.method(
            'database.getCities',
            {
                'q': city_name
            }
        )

        try:
            cities = cities['items']
        except KeyError:
            return []

        res = []

        if cities:
            for city in cities:
                if city_name == city['title'].lower():
                    res.append({
                        'id': int(city['id']),
                        'title': city['title']
                    })
            print(res)
            return res[0]
        else:
            return []


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(220183563)
    users = bot.serch_users(params)
    user = users.pop()
    photos = bot.get_photos(user['id'])
    # print(user)
    # print(photos)
