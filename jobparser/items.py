# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    photo = scrapy.Field()
    owner_id = scrapy.Field()
    search_type = scrapy.Field()


"""
Старый items к 7 уроку:
"""

def raw_into_str(raw_data):
    """Функция для очистки строк характеристик товара от лишних символов"""
    new_data = raw_data.strip('\n ')
    if new_data:
        return new_data


def price_to_digit(raw_price):
    """Функция для перевода строкового значения цены в числовое"""
    price = raw_price.replace(' ', '')
    if price.isdigit():
        return int(price)
    return price


class LeroyparserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(output_processor=TakeFirst(),  # лямбда переводит цену в число с проверкой
                         input_processor=MapCompose(price_to_digit))
    link = scrapy.Field(output_processor=TakeFirst())
    specs = scrapy.Field(input_processor=MapCompose(raw_into_str))
    _id = scrapy.Field()


"""
Старые items к 6 уроку:
"""


class JobparserItem(scrapy.Item):
    name = scrapy.Field()
    salary = scrapy.Field()
    link = scrapy.Field()
    min = scrapy.Field()
    max = scrapy.Field()
    cur = scrapy.Field()
    _id = scrapy.Field()


class BookparserItem(scrapy.Item):
    name = scrapy.Field()
    authors = scrapy.Field()
    price = scrapy.Field()
    discount_price = scrapy.Field()
    normal_price = scrapy.Field()
    link = scrapy.Field()
    rating = scrapy.Field()
    _id = scrapy.Field()
