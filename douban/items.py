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

class DoubanMovieItem(Item):
    movie_id = Field()
    movie_name = Field()
    director = Field()
    author = Field()
    actors = Field()
    movie_type = Field()
    official_website = Field()
    region_made = Field()
    language = Field()
    date_published = Field()
    movie_length = Field()
    alias = Field()

    votes = Field()
    average_rating = Field()
    stars5_ratings = Field()
    stars4_ratings = Field()
    stars3_ratings = Field()
    stars2_ratings = Field()
    stars1_ratings = Field()

    description = Field()
    awards = Field() # hold on
    recommendations = Field()
    labels = Field()
    collections = Field()
    wishes = Field()

class DoubanReviewItem(DoubanCommentItem):
    useless_votes = Field()
    replies = Field() # hold on
    forwards = Field()
    review_title = Field()
    review_id = Field()
