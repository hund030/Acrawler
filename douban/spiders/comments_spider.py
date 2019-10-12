# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy import Selector
from scrapy.http import Request
from dns_cache import _setDNSCache
from items import DoubanCrawlerItem

class CommentsSpider(Spider):
    name = "comments"

    def __init__(self):
        super(CommentsSpider, self).__init__()
        self.pages = []
        self.count = 0

    def start_requests(self):
        urls = [
            'https://movie.douban.com/subject/26683723/comments?start=0&limit=20&sort=new_score&status=P'# ,
            # 'https://movie.douban.com/subject/26683723/comments?start=0&limit=20&sort=new_score&status=F'
        ]

        for url in urls:
            self.pages.append(url)
            yield Request(url=url, callback=self.parse_next_page, dont_filter=True)

    def parse_next_page(self, response):
        # print(response.xpath('//a[@class="next"]/@href'))
        _setDNSCache()
        next_page = response.urljoin(response.xpath('//a[@class="next"]/@href').extract()[0])
        if next_page and self.count < 10:
            self.count = self.count + 1
            self.pages.append(next_page)
            yield Request(url=next_page, callback=self.parse_next_page, dont_filter=True)
        else:
            for p in self.pages:
                # print("parse_next_page: prepare to parse comments ", p)
                yield Request(url=p, callback=self.parse_comment)

    def parse_comment(self, response):
        _setDNSCache()
        comment = DoubanCrawlerItem()
        # print(response.body)
        for item in response.xpath('//div[@class="comment-item"]'):
            # 短评的唯一id
            comment['comment_id'] = int(item.xpath('div[@class="comment"]/h3/span[@class="comment-vote"]/input/@value').extract()[0].strip())
            # 多少人评论有用
            comment['votes'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-vote"]/span/text()').extract()[0].strip()
            # 状态
            comment['user_status'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[1]/text()').extract()[0].strip()
            # 评分
            comment['rating'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[2]/@class').extract()[0].strip()
            # 评论时间
            comment['comment_time'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[@class="comment-time "]/@title').extract()
            # 评论内容
            comment['content'] = item.xpath('div[@class="comment"]/p/span[@class="short"]/text()').extract()[0].strip()
            # 评论者名字（唯一）
            comment['user_name'] = item.xpath('div[@class="avatar"]/a/@title').extract()[0]
            # 评论者页面
            comment['user_url'] = item.xpath('div[@class="avatar"]/a/@href').extract()[0]

            yield comment
