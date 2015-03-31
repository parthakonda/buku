from rest_framework import serializers
from .models import PublicCategories, PrivateCategories, FeedMapper, Feeds, UserSubscriptions, FeedStatus, UserSubscriptions

#Default Serializers
class FeedStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedStatus

class UserSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscriptions

class PublicCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicCategories

class PrivateCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateCategories
        
class FeedMapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedMapper

class FeedsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feeds

class UserSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscriptions

#Create Serializer
class PrivateCategoriesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateCategories
        fields = ('name', 'description')

#List Serializer
class UserSubscriptionsListSerializer(serializers.ModelSerializer):
    feed = serializers.SerializerMethodField('getFeedUrl')
    category = serializers.SerializerMethodField('getCategory')
    
    def getFeedUrl(self, obj):
        return {'pk':obj.feeds.pk, 'url':obj.feeds.url, 'feedurl':obj.feeds.feed_url }

    def getCategory(self, obj):
        if obj.category is not None:
            return {'pk':obj.category.pk, 'name':obj.category.name, 'description':obj.category.description }
        else:
            return {'pk':'', 'name':'', 'description':'' }

    class Meta:
        model = UserSubscriptions
