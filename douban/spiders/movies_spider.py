# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy import Selector
from scrapy.http import Request
from douban.dns_cache import _setDNSCache
from douban.items import DoubanCrawlerItem
from selenium import webdriver

class MoviesSpider(Spider):
    name = "movies"

    def __init__(self):
        super(MoviesSpider, self).__init__()
        # self.pages = []
        self.count = 0

    def start_requests(self):
        urls = [
            'https://movie.douban.com/explore#!type=movie&tag=%E7%88%B1%E6%83%85&sort=recommend&page_limit=20&page_start=0'
        ]

        for url in urls:
            # self.pages.append(url)
            yield Request(url=url, callback=self.parse_movies)

    def parse_movies(self, response):
        # print(response.xpath('//a[@class="next"]/@href'))
        _setDNSCache()
        filename = "movies_page.html"
        with open(filename, 'wb') as f:
            f.write(response.body)