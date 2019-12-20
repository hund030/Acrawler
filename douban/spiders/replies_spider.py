# -*- coding: utf-8 -*-

from scrapy import Spider, Selector
from scrapy.http import Request
from douban.dns_cache import _setDNSCache
from douban.items import DoubanReplyItem
from urllib.parse import urljoin

class RepliesSpider(Spider):
    name = "replies"

    def __init__(self):
        super(RepliesSpider, self).__init__()
    
    def start_requests(self):
        with open('index.txt') as f:
            for i in f:
                url = 'https://movie.douban.com/subject/' + i.rstrip('\n') + '/reviews'
                yield Request(url=url, callback=self.parse_reviews)

    def parse_reviews(self, response):
        _setDNSCache()

        for item in response.xpath('//div[@class="main review-item"]'):
            url = item.xpath('div/h2/a/@href').get()
            yield Request(url=url, callback=self.parse_replies, meta={
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 5}
                    }
                })
            # TODO::next page
            url = urljoin(response.url, response.xpath('//span[@class="next"]/link/@href').get())
            if url:
                yield Request(url=url, callback=self.parse_reviews)
    
    def parse_replies(self, response):
        _setDNSCache()

        # crawl replies
        reply = DoubanReplyItem()

        for item in response.xpath('//div[@class="item comment-item"]'):
            #回复对应的电影id
            reply['movie_id'] = response.url.split('/')[4]
            #回复的id
            reply['reply_id'] = item.xpath('@data-cid').get()
            #回复时间
            reply['reply_time'] = item.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/time/text()').get()
            #回复内容
            reply['content'] = []
            for c in item.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="comment-content"]/span/node()'):
                if c.xpath('text()').get():
                    reply['content'].append(c.xpath('text()').get().strip())
                elif c.get().strip() != '<br>' and c.get().strip != '':
                    reply['content'].append(c.get().strip())
            #回复者名字
            reply['user_name'] = item.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a/text()').get()
            #回复者id
            reply['user_id'] = item.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a[1]/@href').get().split('/')[4]
            #所回复的回复的id(如本条回复直接回复到影评，则没有)
            reply['reply_to'] = ''

            yield reply

            try:
                reply_list = item.xpath('div[@class="reply-list"]')
                parent_id = reply['reply_id']

                for i in reply_list.xpath('div[@class="item reply-item"]'):
                    reply['movie_id'] = response.url.split('/')[4]
                    reply['reply_id'] = i.xpath('@data-cid').get()
                    reply['reply_time'] = i.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/time/text()').get()
                    reply['content'] = []
                    for c in i.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="comment-content"]/span/node()'):
                        if c.xpath('text()').get():
                            reply['content'].append(c.xpath('text()').get().strip())
                        elif c.get().strip() != '<br>' and c.get().strip != '':
                            reply['content'].append(c.get().strip())
                    reply['user_name'] = i.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a/text()').get()
                    reply['user_id'] = i.xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a[1]/@href').get().split('/')[4]
                    reply['reply_to'] = parent_id
                    yield reply
            except:
                pass
                
        try:
            next_page = response.urljoin(response.xpath('//a[@class="next"]/@href').extract()[0])
        except:
            next_page = ''

        if next_page:
            yield Request(url=next_page, callback=self.parse_replies)
