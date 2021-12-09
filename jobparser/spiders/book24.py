import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=испанский%20язык',
                  'https://book24.ru/search/?q=испанский%20язык', ]
    count = 2

    def parse(self, response: HtmlResponse, **kwargs):
        url = f'https://book24.ru/search/page-{self.count}/?q=испанский%20язык'
        if url:
            yield scrapy.Request(url=url, callback=self.parse)
        self.count += 1
        links = response.xpath('//div[@class="product-card__content"]/a/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    @staticmethod
    def book_parse(response: HtmlResponse):
        name = response.xpath('//h1//text()').get()
        authors = response.xpath('(//a[@class="product-characteristic-link smartLink"])[1]//text()').getall()

        price = response.xpath("(//span[@class='app-price product-sidebar-price__price-old'])//text()").getall()
        price += response.xpath("(//span[@class='app-price product-sidebar-price__price'])//text()").getall()

        link = response.url
        rating = response.xpath('//span[@class="rating-widget__main-text"]//text()').get()
        item = BookparserItem(name=name, price=price, link=link,
                              rating=rating, authors=authors)
        yield item
