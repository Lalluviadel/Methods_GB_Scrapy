"""
Модуль для выполнения запросов к полученной базе данных.
+ 5) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
+ 6) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
"""
from pprint import pprint

from pymongo import MongoClient


def get_data(user_id):
    """Функция для получения данных из базы.
    У каждого документа есть поле 'owner_id', которое хранит id пользователя,
    с чьей страницы мы собирали данные. Коллекции базы называются 'followers'
    и 'following', в одной хранятся подписчики всех пользователей, со страниц
    которых мы получали данные, в другой - подписки.
    Выбирая нужные значения при составлении апроса, мы получим результат.
    """
    client = MongoClient('localhost', 27017)
    db = client.insta_friendship
    collections = ['followers', 'following']
    for col in collections:
        collection = db[col]
        cursor = collection.find({'owner_id': user_id})
        print(f'Список всех {col} пользователя {user_id}:')
        for record in cursor:
            pprint(record)
