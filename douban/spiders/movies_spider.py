# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy import Selector
from scrapy.http import Request
from douban.dns_cache import _setDNSCache
from douban.items import DoubanMovieItem

class MoviesSpider(Spider):
    name = "movies"

    def __init__(self):
        super(MoviesSpider, self).__init__()
        # self.pages = []
        self.count = 0

    def start_requests(self):
        with open('index.txt') as f:
            for i in f:
                url = 'https://movie.douban.com/subject/' + i.rstrip('\n')
                # self.pages.append(url)
                yield Request(url=url, callback=self.parse_movies)

    def parse_movies(self, response):
        # print(response.xpath('//a[@class="next"]/@href'))
        _setDNSCache()

        movie = DoubanMovieItem()
        movie['movie_id'] = response.url.split('/')[4]
        # movie['movie_name'] = response.xpath('//div[@id="content"]/h1/span[1]/text()').extract()[0].strip()
        movie['movie_name'] = response.xpath('//title/text()').get().rstrip().strip('\n').strip()[:-4].rstrip()

        movie_info = response.xpath('//div[@id="info"]')
        movie['director'] = movie_info.xpath('span[1]/span[@class="attrs"]/a/text()').getall()
        movie['author'] = movie_info.xpath('span[2]/span[@class="attrs"]/a/text()').getall()
        movie['actors'] = movie_info.xpath('span[@class="actor"]/span[@class="attrs"]/a/text()').getall()
        movie['movie_type'] = movie_info.xpath('span[@property="v:genre"]/text()').getall()
        movie['official_website'] = movie_info.xpath('span[@class="pl" and text()="官方网站:"]/following-sibling::a/text()').get()
        movie['region_made'] = movie_info.xpath('span[@class="pl" and text()="制片国家/地区:"]/following-sibling::text()').get()
        movie['language'] = movie_info.xpath('span[@class="pl" and text()="语言:"]/following-sibling::text()').get()
        movie['date_published'] = movie_info.xpath('span[@property="v:initialReleaseDate"]/text()').get()
        movie['movie_length'] = movie_info.xpath('span[@property="v:runtime"]/text()').get()
        movie['alias'] = movie_info.xpath('span[@class="pl"][6]/following-sibling::text()').get()

        # movie['votes'] = response.xpath('//div[@class="rating_self clearfix"]/div[@class="rating_right"]/div[@class="rating_sum"]/a/span/text()').get()
        movie['votes'] = response.xpath('//span[@property="v:votes"]/text()').get()
        movie['average_rating'] = response.xpath('//div[@class="rating_self clearfix"]/strong/text()').get()
        movie['stars5_ratings'] = response.xpath('//div[@class="ratings-on-weight"]/div[@class="item"][1]/span[@class="rating_per"]/text()').get()
        movie['stars4_ratings'] = response.xpath('//div[@class="ratings-on-weight"]/div[@class="item"][2]/span[@class="rating_per"]/text()').get()
        movie['stars3_ratings'] = response.xpath('//div[@class="ratings-on-weight"]/div[@class="item"][3]/span[@class="rating_per"]/text()').get()
        movie['stars2_ratings'] = response.xpath('//div[@class="ratings-on-weight"]/div[@class="item"][4]/span[@class="rating_per"]/text()').get()
        movie['stars1_ratings'] = response.xpath('//div[@class="ratings-on-weight"]/div[@class="item"][5]/span[@class="rating_per"]/text()').get()

        movie['description'] = response.xpath('//span[@property="v:summary"]/text()').getall()
        movie['recommendations'] = response.xpath('//div[@class="recommendations-bd"]/dl/dd/a/text()').getall()
        movie['labels'] = response.xpath('//div[@class="tags-body"]/a/text()').getall()
        movie['collections'] = response.xpath('//div[@class="subject-others-interests-ft"]/a[1]/text()').get()
        movie['wishes'] = response.xpath('//div[@class="subject-others-interests-ft"]/a[2]/text()').get()

        yield movie
