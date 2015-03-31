from django.db import models
from core.authentication.models import Users

class PublicCategories(models.Model):

    name = models.CharField(max_length = 30)
    description = models.CharField(max_length = 200, null = True)
    
    class Meta:
        db_table = "public_feed_categories"

class PrivateCategories(models.Model):

    name = models.CharField(max_length = 30)
    description = models.CharField(max_length = 200, null = True)
    user = models.ForeignKey(Users, related_name="created_by", null = True)

    class Meta:
        db_table = "private_feed_categories"

class FeedMapper(models.Model):
    url = models.URLField(unique = True)
    feed_url = models.URLField()

    class Meta:
        db_table = "feed_mapper"

class Feeds(models.Model):
    feed = models.ForeignKey(FeedMapper, related_name = "feedurl")
    feedid = models.URLField(unique = True)
    feed_title = models.TextField()
    feed_image = models.URLField()
    feed_summary = models.TextField(null = True)
    feed_content = models.TextField(null = True)
    feed_link = models.URLField()

    class Meta:
        db_table = "feeds"
 
class UserSubscriptions(models.Model):
    user = models.ForeignKey(Users, related_name="subscribed_user", null = True) 
    feeds = models.ForeignKey(FeedMapper, related_name = "subscription")
    category = models.ForeignKey(PrivateCategories, related_name="feed_catgory", null = True)

    class Meta:
        db_table = "user_subscriptions"

class FeedStatus(models.Model):
    user = models.ForeignKey(Users, related_name="feed_user") 
    feed = models.ForeignKey(Feeds, related_name="feed_feed") 
    status = models.CharField(max_length = 20, null = True)

    class Meta:
        db_table = "feed_status"