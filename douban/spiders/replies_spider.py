# -*- coding: utf-8 -*-

from scrapy import Spider, Selector
from scrapy.http import Request
from douban.dns_cache import _setDNSCache
from douban.items import DoubanReplyItem
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class RepliesSpider(Spider):
    name = "replies"

    def __init__(self):
        options = Options()
        options.headless = True
        fp = webdriver.FirefoxProfile()
        fp.set_preference('permissions.default.image', 2)
        fp.set_preference('permissions.default.stylesheet', 2)
        fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        self.driver = webdriver.Firefox(options=options, firefox_profile=fp, executable_path=r'/home/hund030/geckodriver')
        super(RepliesSpider, self).__init__()
    
    def start_requests(self):
        with open('index.txt') as f:
            for i in f:
                url = 'https://movie.douban.com/subject/' + i.rstrip('\n') + '/reviews'
                yield Request(url=url, callback=self.parse_reviews)
                break

    def parse_reviews(self, response):
        _setDNSCache()

        for item in response.xpath('//div[@class="main review-item"]'):
            url = item.xpath('div/h2/a/@href').get()
            yield Request(url=url, callback=self.parse_replies)
            break
            # TODO::next page
            url = urljoin(response.url, response.xpath('//span[@class="next"]/link/@href').get())
            if url:
                yield Request(url=url, callback=self.parse_reviews)
    
    def parse_replies(self, response):
        _setDNSCache()
        self.driver.get(response.url)
        self.driver.implicitly_wait(5)

        # crawl replies
        reply = DoubanReplyItem()
        try:
            comments = self.driver.find_elements_by_xpath('//div[@class="item comment-item"]')
        except:
            comments = []

        for item in comments:
            #回复对应的电影id
            reply['movie_id'] = response.url.split('/')[4]
            #回复的id
            reply['reply_id'] = item.get_attribute('data-cid')
            #回复时间
            reply['reply_time'] = item.find_element_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/time').text
            #回复内容
            reply['content'] = []
            for c in item.find_elements_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="comment-content"]/span'):
                if c.text.strip() != '<br>' and c.text.strip != '':
                    reply['content'].append(c.text.strip())
            #回复者名字
            reply['user_name'] = item.find_element_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a').text
            #回复者id
            reply['user_id'] = item.find_element_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a[1]').get_attribute("href").split('/')[4]
            #所回复的回复的id(如本条回复直接回复到影评，则没有)
            reply['reply_to'] = ''

            yield reply

            try:
                reply_list = item.find_element_by_xpath('div[@class="reply-list"]')
                parent_id = reply['reply_id']
                # yield self.parse_reply_list(reply_list, reply["reply_id"])
                try:
                    get_more = reply_list.find_element_by_xpath('div[@class="replies-list-control"]/button')
                    get_more.click()
                    self.driver.implicitly_wait(5)
                except:
                    pass

                for item in reply_list.find_elements_by_xpath('div[@class="item reply-item"]'):
                    reply['movie_id'] = item.get_attribute('data-target_id')
                    reply['reply_id'] = item.get_attribute('data-cid')
                    reply['reply_time'] = item.find_element_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/time').text
                    reply['content'] = []
                    for c in item.find_elements_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="comment-content"]/span'):
                        if c.text.strip() != '<br>' and c.text.strip != '':
                            reply['content'].append(c.text.strip())
                    reply['user_name'] = item.find_element_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a').text
                    reply['user_id'] = item.find_element_by_xpath('div[@class="comment-item-body"]/div[@class="comment-main"]/div[@class="meta-header"]/a[1]').get_attribute("href").split('/')[4]
                    reply['reply_to'] = parent_id
                    yield reply

            except:
                pass
            break
                
        try:
            next_page = response.urljoin(self.driver.find_element_by_xpath('//a[@class="next"]').get_attribute("href"))
        except:
            next_page = ""

        if next_page:
            yield Request(url=next_page, callback=self.parse_replies)
