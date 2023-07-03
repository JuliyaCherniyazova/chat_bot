
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import add_user, read_users, engine


class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method(
            'messages.send',
            {
                'user_id': user_id,
                'message': message,
                'attachment': attachment,
                'random_id': get_random_id()
            })

    def take_user(self, users, event):
        user = users.pop()
        while read_users(engine, self.params['id'], user['id']):
            user = users.pop()
        photos_user = self.api.get_photos(user['id'])

        add_user(engine, self.params['id'], user['id'])
        self.message_send(
            event.user_id,
            f'Встречайте {user["name"]} https://vk.com/id{user["id"]}',
            attachment=photos_user
        )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if (command == 'привет') or (command == 'привет!'):
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]} \n'
                                                     f'Давайте начнем поиск (напишите команду поиск)')

                elif command == 'поиск':
                    if self.params:
                        if (self.params['bdate'] is None) or (len(self.params['bdate'].split('.')) != 3):
                            self.message_send(
                                event.user_id,
                                'Введите дату вашего рождения (Обязательно так: дд.мм.год)'
                            )
                        elif self.params['city'] is None:
                            self.message_send(
                                event.user_id,
                                'В каком городе ищем? \n'
                                '(Напишите название города такой командой (Город.(название города)))'
                            )
                        else:
                            users = self.api.serch_users(self.params)
                            user = users.pop()
                            while read_users(engine, self.params['id'], user['id']):
                                user = users.pop()

                            photos_user = self.api.get_photos(user['id'])

                            add_user(engine, self.params['id'], user['id'])

                            self.message_send(
                                event.user_id,
                                f'Встречайте {user["name"]} https://vk.com/id{user["id"]}',
                                attachment=photos_user
                            )
                    else:
                        self.message_send(event.user_id, 'Для начала давайте поздороваемся. (Напиши мне привет)')

                elif len(command.split('.')) == 3:
                    if command.split('.')[0].isdigit() and command.split('.')[1].isdigit() and command.split('.')[2].isdigit():
                        if int(command.split('.')[0]) > 31:
                            self.message_send(event.user_id, 'Неверно введена дата')
                        elif int(command.split('.')[1]) > 12:
                            self.message_send(event.user_id, 'Неверно введена дата')
                        else:
                            self.params['bdate'] = command
                            self.message_send(event.user_id, 'Давайте начнем поиск (напишите команду поиск)')
                    else:
                        self.message_send(event.user_id, 'Неверно введена дата')

                elif command.split('.')[0] == 'город':
                    city_name = command.split('.')[1]
                    city = self.api.get_city_id(city_name)
                    if city:
                        self.params['city'] = city['id']
                        self.message_send(event.user_id, 'Давайте начнем поиск (напишите команду поиск)')
                    else:
                        self.message_send(event.user_id, 'Такого города не существует')

                elif command == 'ещё' or command == 'еще':
                    if self.params:
                        if users:
                            self.take_user(users, event)
                        else:
                            self.offset += 50
                            users = self.api.serch_users(self.params, self.offset)
                            self.take_user(users, event)
                    else:
                        self.message_send(event.user_id, 'Для начала давайте поздороваемся. (Напиши мне привет)')

                elif command == 'сменить город':
                    self.message_send(
                        event.user_id,
                        'В каком городе ищем? \n'
                        '(Напишите название города такой командой (Город.(название города)))'
                    )

                elif command == 'команды':
                    self.message_send(
                        event.user_id,
                        'привет - обязательно надо поздороваться. \n'
                        'поиск - начинаем искать вторую половинку) \n'
                        'ещё - просмотр следующей кандидатуры. \n'
                        'пока - завершение работы (после этой команды снова надо поздороваться) \n'
                        'сменить город - меняет город поиска'
                    )

                elif command == 'пока':
                    self.params = []
                    self.message_send(event.user_id, 'пока')

                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()