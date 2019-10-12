from scrapy.item import Item, Field

class DoubanCrawlerItem(Item):
    user_name = Field()
    user_url = Field()
    content = Field()
    votes = Field()
    user_status = Field()
    rating = Field()
    comment_time = Field()
    comment_id = Field()
