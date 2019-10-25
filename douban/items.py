from scrapy.item import Item, Field

class DoubanCommentItem(Item):
    user_name = Field()
    user_id = Field()
    content = Field()
    votes = Field()
    user_status = Field()
    rating = Field()
    comment_time = Field()
    comment_id = Field()
    movie_id = Field()