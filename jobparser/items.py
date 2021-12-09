# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
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
