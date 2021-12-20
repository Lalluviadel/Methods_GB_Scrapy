# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

# from pprint import pprint

import scrapy
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from scrapy.pipelines.images import ImagesPipeline


class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.insta_friendship

    def process_item(self, item, spider):
        """Добавляем документ в коллекцию followers или following в зависимости от содержимого поля"""
        collection = self.mongobase[item['search_type']]
        # collection.drop()
        try:
            collection.update_one({'user_id': item['user_id']}, {'$set': item}, upsert=True)
        except DuplicateKeyError as e:
            print(e, item['user_id'])

        return item


class InstaImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            try:
                yield scrapy.Request(item['photo'])
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        """Создаем путь к аватаркам подписчиков и подписок вида:
        photos/id нашего основного пользователя/followers или following/id пользователя с аватарки.jpg
        В итоге получается папка для каждого пользователя-объекта скрапинга, в которой
        две подпапки для подписчиков и подписок
        """
        return f'{item["owner_id"]}/{item["search_type"]}/{item["user_id"]}.jpg'

# class LeroyParserPipeline:
#     """ Pipeline для leroymerlin.ru"""
#
#     def __init__(self):
#         client = MongoClient('localhost', 27017)
#         self.mongobase = client.leroy_products
#
#     def process_item(self, item, spider):
#         collection = self.mongobase[spider.name]
#         # collection.drop()
#         item['specs'] = self.process_specs(item['specs'])
#         try:
#             collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
#         except DuplicateKeyError as e:
#             print(e, item['link'])
#         return item
#
#     @staticmethod
#     def process_specs(raw_list):
#         """Превращаем список характеристик в словарь"""
#         specs_dict = dict(zip(raw_list[::2], raw_list[1::2]))
#         # pprint(specs_dict)
#         return specs_dict
#
#
# class LeroyImagesPipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         if item['photos']:
#             for img in item['photos']:
#                 try:
#                     yield scrapy.Request(img)
#                 except Exception as e:
#                     print(e)
#
#     def item_completed(self, results, item, info):
#         item['photos'] = [i[1] for i in results if i[0]]
#         return item
#
#     def file_path(self, request, response=None, info=None, *, item=None):
#         img_name = str(request.url).split('/')[-1].strip('.jpg')
#         product_id = str(item['link']).split('/')[-2].split('-')[-1]
#         return f'full/{product_id}/{img_name}.jpg'

# class JobparserPipeline:
#     """ Pipeline для вакансий"""
#
#     def __init__(self):
#         client = MongoClient('localhost', 27017)
#         self.mongobase = client.vacancy0712
#
#     def process_item(self, item, spider):
#         collection = self.mongobase[spider.name]
#
#         # collection.drop()
#         # для hh.ru
#         if spider.name == 'hhru':
#             item['min'], item['max'], item['cur'] = self.hh_process_salary(item['salary'])
#         # для superjob.ru
#         else:
#             item['min'], item['max'], item['cur'] = self.sj_process_salary(item['salary'])
#
#         del (item['salary'])
#         try:
#             collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
#         except DuplicateKeyError as e:
#             print(e)
#
#     # для hh.ru
#     @staticmethod
#     def hh_process_salary(salary):
#         # работаем с вакансиями, где информация о зарплате есть
#         if len(salary) > 1:
#             # где оба поля можно заполнить
#             if salary[2] == ' до ':
#                 salary_min = int(salary[1].replace('\xa0', ''))
#                 salary_max = int(salary[3].replace('\xa0', ''))
#                 currency = salary[5]
#             # указана только максимальная
#             elif salary[0] == 'до ':
#                 salary_min, salary_max, currency = None, int(salary[1].replace('\xa0', '')), salary[3]
#             # указана только минимальная
#             else:
#                 salary_min, salary_max, currency = int(salary[1].replace('\xa0', '')), None, salary[3]
#         # для вакансий, где информации о зарплате нет или указано 'Договорная' и т.д.
#         else:
#             salary_min, salary_max, currency = None, None, None
#         return salary_min, salary_max, currency
#
#     @staticmethod
#     # для superjob.ru
#     def sj_process_salary(salary):
#         # работаем с вакансиями, где информация о зарплате есть
#         if len(salary) > 1:
#             # где оба поля указаны на superjob
#             if len(salary) > 3:
#                 salary_min = int(salary[0].replace('\xa0', ''))
#                 salary_max = int(salary[4].replace('\xa0', ''))
#                 currency = salary[6]
#             # указана только минимальная
#             elif salary[0] == 'от':
#                 salary_and_curr = salary[2].split('\xa0')
#                 salary_min = int(salary_and_curr[0] + salary_and_curr[1])
#                 salary_max = None
#                 currency = salary_and_curr[2]
#             # указана только максимальная
#             elif salary[0] == 'до':
#                 salary_and_curr = salary[2].split('\xa0')
#                 salary_min = None
#                 salary_max = int(salary_and_curr[0] + salary_and_curr[1])
#                 currency = salary_and_curr[2]
#             # указана фиксированная
#             else:
#                 sal = int(salary[0].replace('\xa0', ''))
#                 salary_min, salary_max, currency = sal, sal, salary[2]
#         # для вакансий, где информации о зарплате нет или указано 'Договорная' и т.д.
#         else:
#             salary_min, salary_max, currency = None, None, None
#         return salary_min, salary_max, currency
#
#
# class BookparserPipeline:
#     """ Pipeline для книг"""
#
#     def __init__(self):
#         client = MongoClient('localhost', 27017)
#         self.mongobase = client.books0712
#
#     def process_item(self, item, spider):
#         collection = self.mongobase[spider.name]
#         # collection.drop()
#
#         # для labirint.ru
#         if spider.name == 'labirint':
#             item['name'] = self.name_processing(item['name'])
#             item['authors'] = self.authors_processing(item['authors'])
#             item['rating'] = float(item['rating'])
#             item['normal_price'], item['discount_price'] = self.price_processing(item['price'])
#         # для book24.ru
#         else:
#             item['name'] = item['name'].strip(' ')
#             item['normal_price'], item['discount_price'] = self.price_processing(item['price'])
#             item['rating'] = float(item['rating'].strip(' ').replace(',', '.'))
#
#         del (item['price'])
#         try:
#             collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
#         except DuplicateKeyError as e:
#             print(e)
#
#     @staticmethod
#     def name_processing(name):
#         try:
#             name = name.split(':')[1]
#         finally:
#             return name
#
#     @staticmethod
#     def authors_processing(authors):
#         try:
#             authors.remove('Автор: ')
#         except Exception:
#             return 'Без автора'
#
#         def condition(x):
#             # очистка списка с авторами от мусора
#             return x != '\xa0' and x != ' скрыть' \
#                    and x != ' все' and x != ', '
#
#         result = [x for x in authors if condition(x)]
#         return result
#
#     @staticmethod
#     def price_processing(price):
#         # универсальный метод для двух сайтов для многоступенчатой обработки данных о ценах
#         price_1_step = list(map(lambda x: x.strip(' ₽'), price))
#         try:
#             price_2_step = list(map(lambda x: x.replace('\xa0', ''), price_1_step))
#         except Exception:
#             price_2_step = price_1_step
#         finally:
#             if len(price_2_step):
#                 if len(price_2_step) > 1:
#                     old_price, new_price = price_2_step
#                 else:
#                     old_price, new_price = price_2_step[0], price_2_step[0]
#             else:
#                 return None, None
#         return int(old_price), int(new_price)
