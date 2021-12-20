"""
+ 1) Написать приложение, которое будет проходиться по указанному списку двух и/или более пользователей
и собирать данные об их подписчиках и подписках.
+ 2) По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект
нужно извлечь имя, id, фото (остальные данные по желанию). Фото можно дополнительно скачать.
+ 4) Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее продумать, чтобы:
+ 5) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
+ 6) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

Для выполнения данной работы необходимо делать запросы в апи инстаграм с указанием заголовка User-Agent :
'Instagram 155.0.0.37.107'
"""

import json
import re
from copy import deepcopy
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import InstaparserItem
from jobparser.my_personal_data import my_pwd, my_login


class InstagramSpider(scrapy.Spider):
    name = 'instagram_friendship'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    """Для сохранения конфиденциальности, свой логин и пароль я загружаю
    из отдельного файла, который помещен в .gitignore, директория с полученными 
    фото также помещена в .gitignore, чтобы не засорять репозиторий"""

    inst_login = my_login
    inst_pwd = my_pwd
    user = ['angelikazujkina', 'parshkiss']
    inst_friends_link = 'https://i.instagram.com/api/v1/friendships/'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_pwd},
                                 headers={'x-csrftoken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):

            for user in self.user:
                """Выполняем сбор данных для каждого полльзователя из заданного списка"""
                yield response.follow(
                    f'/{user}',
                    callback=self.user_parse,
                    cb_kwargs={'username': user}
                )

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12, 'max_id': 0, 'search_surface': 'follow_list_page'}
        search_type = ['followers', 'following']
        for s_type in search_type:
            """Выполняем сбор данных для каждого направления поиска (подписчики и подписки)"""
            friends = f'{self.inst_friends_link}{user_id}/{s_type}/?&{urlencode(variables)}'
            yield scrapy.Request(friends,
                                 method='GET',
                                 callback=self.user_friends_parse,
                                 headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                 cb_kwargs={'username': username,
                                            'user_id': user_id,
                                            's_type': s_type,
                                            'variables': deepcopy(variables)}
                                 )

    def user_friends_parse(self, response: HtmlResponse, username, user_id, s_type, variables):
        j_data = response.json()
        users = j_data.get('users')
        for user in users:
            """Выполняем сбор данных, начиная с первых 12 полученных пользователей"""
            item = InstaparserItem(
                user_id=user.get('pk'),
                username=user.get('username'),
                full_name=user.get('full_name'),
                photo=user.get('profile_pic_url'),
                owner_id=user_id,
                search_type=s_type,
            )
            yield item

        if j_data.get('big_list'):
            """Выполняем запрос, пока big_list=True, у последнего запроса эта переменная равняется False"""
            # print(variables['max_id'])
            """Каждый проход увеличиваем max_id в запросе на 12, чтобы получить следующих пользователей"""
            variables['max_id'] += 12
            friends = f'{self.inst_friends_link}{user_id}/{s_type}/?&{urlencode(variables)}'
            yield scrapy.Request(friends,
                                 method='GET',
                                 callback=self.user_friends_parse,
                                 headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                 cb_kwargs={'username': username,
                                            'user_id': user_id,
                                            's_type': s_type,
                                            'variables': deepcopy(variables)}
                                 )

    @staticmethod
    def fetch_csrf_token(text):
        """ Get csrf-token for auth """
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    @staticmethod
    def fetch_user_id(text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
