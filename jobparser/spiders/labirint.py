"""
II вариант
1) Создать пауков по сбору данных о книгах с сайтов labirint.ru и/или book24.ru
2) Каждый паук должен собирать:
* Ссылку на книгу
* Наименование книги
* Автор(ы)
* Основную цену
* Цену со скидкой
* Рейтинг книги
3) Собранная информация должна складываться в базу данных
"""

import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/испанский%20язык/?stype=0',
                  'https://www.labirint.ru/search/испанский%20язык/?stype=0', ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath('//a[@class="pagination-next__text"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@class="product-title-link"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    @staticmethod
    def book_parse(response: HtmlResponse):
        name = response.xpath('//h1//text()').get()
        authors = response.xpath('(//div[@class="authors"])[1]//text()').getall()

        price = response.xpath("(//span[@class='buying-price-val-number'])//text()").getall()
        if not price:
            price = response.xpath("(//span[@class='buying-priceold-val-number'])//text()").getall()
            price += response.xpath("(//span[@class='buying-pricenew-val-number'])//text()").getall()

        link = response.url
        rating = response.xpath('//div[@id="rate"]//text()').get()
        item = BookparserItem(name=name, price=price, link=link,
                              rating=rating, authors=authors)
        yield item
