# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy import Selector
from scrapy.http import Request
from douban.dns_cache import _setDNSCache
from douban.items import DoubanCommentItem

class ReviewsSpider(Spider):
    name = "reviews"

    def __init__(self):
        super(ReviewsSpider, self).__init__()
        # self.pages = []
        self.count = 0

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

        main = article.xpath('//div[@class="main"]')
        review['user_name'] = main.xpath('header[@class="main-hd"]/a[1]/span/text()').get()
        review['user_id'] = main.xpath('header[@class="main-hd"]/a[1]/span/@href').split('/')[4]
        review['movie_id'] = main.xpath('header[@class="main-hd"]/a[2]/span/@href').split('/')[4]
        # TODO:: review may don't have a rating
        review['rating'] = main.xpath('header[@class="main-hd"]/span[1]/@class').get().split(' ')[0]
        review['comment_time'] = main.xpath('header[@class="main-hd"]/span[@class="main-meta"]/text()').get()

        review['content'] = main.xpath('//div[@id="link-report"]/div[@class="review-content clearfix"]/p/text()').get()

        review['votes'] = main.xpath('//div[@class="main-panel-useful"]/button[1]/text()').get().strip().rstrip()
        review['useless_votes'] = main.xpath('//div[@class="main-panel-useful"]/button[2]/text()').get().strip().rstrip()
        review['forwards'] = main.xpath('//div[@class="rec-num"]/text()').get()


    def parse_reviews(self, response):
        _setDNSCache()

        for item in response.xpath('//div[@class="review-list"]/div'):
            url = item.xpath('div[@class="main review-item"]/div/h2/a/@href')
            yield Request(url=url, callback=self.parse_review_details)