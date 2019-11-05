# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy import Selector
from scrapy.http import Request
from douban.dns_cache import _setDNSCache
from douban.items import DoubanCommentItem

class CommentsSpider(Spider):
    name = "comments"

    def __init__(self):
        super(CommentsSpider, self).__init__()
        # self.pages = []
        self.count = 0

    def start_requests(self):
        with open('index.txt') as f:
            for i in f:
                url = 'https://movie.douban.com/subject/' + i.rstrip('\n') + '/comments?start=0&limit=20&sort=new_score&status=P'
                # self.pages.append(url)
                yield Request(url=url, callback=self.parse_comments)

    def parse_comments(self, response):
        _setDNSCache()

        # crawl comments
        comment = DoubanCommentItem()
        # print(response.body)
        for item in response.xpath('//div[@class="comment-item"]'):
            # 短评对应的电影id
            comment['movie_id'] = response.url.split('/')[4]
            # 短评的唯一id
            comment['comment_id'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-vote"]/input/@value').extract()[0].strip()
            # 多少人评论有用
            comment['votes'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-vote"]/span/text()').extract()[0].strip()
            # 状态
            # comment['user_status'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[1]/text()').extract()[0].strip()
            # 评分
            comment['rating'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[2]/@class').extract()[0].strip()
            if comment['rating'] == 'comment-time':
                comment['rating'] = 'none'
            # 评论日期
            comment['comment_date'] = item.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[@class="comment-time "]/@title').extract()
            # 评论内容
            comment['content'] = item.xpath('div[@class="comment"]/p/span[@class="short"]/text()').extract()[0].strip()
            # 评论者名字（唯一）
            comment['user_name'] = item.xpath('div[@class="avatar"]/a/@title').extract()[0]
            # 评论者页面
            comment['user_id'] = item.xpath('div[@class="avatar"]/a/@href').extract()[0].split('/')[4]

            yield comment

        # try next page
        try:
            next_page = response.urljoin(response.xpath('//a[@class="next"]/@href').extract()[0])
        except:
            next_page = ''
        if next_page:
            # self.pages.append(next_page)
            yield Request(url=next_page, callback=self.parse_comments)

