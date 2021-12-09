"""
I вариант
1) Доработать паука в имеющемся проекте, чтобы он формировал item по структуре:
*Наименование вакансии
*Зарплата от
*Зарплата до
*Ссылку на саму вакансию
И складывал все записи в БД(любую)

2) Создать в имеющемся проекте второго паука по сбору вакансий с сайта superjob. Паук должен формировать item'ы
по аналогичной структуре и складывать данные также в БД
"""
import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    # start_urls = ['https://izhevsk.hh.ru/search/vacancy?area=1&search_field=name&search_field='
    #               'company_name&search_field=description&fromSearchLine=true&text=python',
    #               'https://izhevsk.hh.ru/search/vacancy?area=2&search_field=name&search_field='
    #               'company_name&search_field=description&fromSearchLine=true&text=python']
    start_urls = [
        'https://sevastopol.hh.ru/search/vacancy?clusters=true&area='
        '130&ored_clusters=true&enable_snippets=true&salary=&text=продавец',
        'https://sevastopol.hh.ru/search/vacancy?clusters=true&area='
        '130&ored_clusters=true&enable_snippets=true&salary=&text=продавец',
    ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    @staticmethod
    def vacancy_parse(response: HtmlResponse):
        name = response.xpath('//h1//text()').get()

        # у HH.ru минимум 2 варианта классов для элементов, в которых они помещают зарплату
        # если выражение к основному классу вернет пустой объект, пробуем искать по второму выражению
        salary = response.xpath("//div[@class='vacancy-salary']//text()")
        if salary:
            salary = salary.getall()
        else:
            salary = response.xpath("//div[@class='vacancy-salary vacancy-salary_vacancyconstructor']//text()").getall()

        link = response.url
        item = JobparserItem(name=name, salary=salary, link=link)
        yield item
