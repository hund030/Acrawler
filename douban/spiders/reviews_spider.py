# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy import Selector
from scrapy.http import Request
from urllib.parse import urljoin
from douban.dns_cache import _setDNSCache
from douban.items import DoubanReviewItem

class ReviewsSpider(Spider):
    name = "reviews"

    def __init__(self):
        super(ReviewsSpider, self).__init__()
        # self.pages = []
        self.count = 10

    def start_requests(self):
        with open('index.txt') as f:
            for i in f:
                url = 'https://movie.douban.com/subject/' + i.rstrip('\n') + '/reviews'
                # self.pages.append(url)
                yield Request(url=url, callback=self.parse_reviews)

    def parse_review_details(self, response):
        _setDNSCache()

        # crawl review details
        review = DoubanReviewItem()
        article = response.xpath('//div[@class="article"]')

        review['review_title'] = article.xpath('h1/span/text()').get()
        review['review_id'] = response.url.split('/')[4]

        main = article.xpath('//div[@class="main"]')
        review['user_name'] = main.xpath('header[@class="main-hd"]/a[1]/span/text()').get()
        review['user_id'] = main.xpath('header[@class="main-hd"]/a[1]/@href').get().split('/')[4]
        review['movie_id'] = main.xpath('header[@class="main-hd"]/a[2]/@href').get().split('/')[4]
        # TODO:: review may don't have a rating
        review['rating'] = main.xpath('header[@class="main-hd"]/span[1]/@class').get().split(' ')[0]
        review['comment_time'] = main.xpath('header[@class="main-hd"]/span[@class="main-meta"]/text()').get()

        review['content'] = []
        for c in main.xpath('//div[@id="link-report"]/div/node()'):
            if c.xpath('text()').get():
                review['content'].append(c.xpath('text()').get().strip())
            elif c.get().strip() != '<br>' and c.get().strip() != '':
                review['content'].append(c.get().strip())
        # review['content'] = main.xpath('//div[@id="link-report"]/div/node()').getall()

        review['votes'] = main.xpath('//div[@class="main-panel-useful"]/button[1]/text()').get().strip().split(' ')[1]
        review['useless_votes'] = main.xpath('//div[@class="main-panel-useful"]/button[2]/text()').get().strip().split(' ')[1]
        review['forwards'] = main.xpath('//span[@class="rec-num"]/text()').get()
        yield review


    def parse_reviews(self, response):
        _setDNSCache()

        for item in response.xpath('//div[@class="main review-item"]'):
            url = item.xpath('div/h2/a/@href').get()
            yield Request(url=url, callback=self.parse_review_details)

        # TODO::next page
        url = urljoin(response.url, response.xpath('//span[@class="next"]/link/@href').get())
        if url:
            yield Request(url=url, callback=self.parse_reviews)