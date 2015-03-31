from .serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from buku.restful.viewsets import CustomModelViewSet
from buku.restful.permissions import AdminCheckPermission
from django.http import HttpResponse
from rest_framework.decorators import detail_route
# from core.services.tasks import sendMail
from datetime import datetime
import pytz
from django.conf import settings
import feedparser
from bs4 import BeautifulSoup


#Models and Serializers
from .models import PublicCategories, PrivateCategories, FeedMapper, Feeds, UserSubscriptions, FeedStatus, UserSubscriptions
from .serializers import PublicCategoriesSerializer, PrivateCategoriesSerializer, FeedMapperSerializer, FeedsSerializer, UserSubscriptionsSerializer, PrivateCategoriesCreateSerializer, FeedStatusSerializer, UserSubscriptionsSerializer, UserSubscriptionsListSerializer

class PublicCategoriesViewSet(CustomModelViewSet):
    """ All User profile Management """
    
    queryset = PublicCategories.objects.all()
    
    parser = {
        'default':PublicCategoriesSerializer
    }

    
    filter_fields = ('name',)
    
    def filtering(self, params, queryset, user = None):
        if "name" in params and params['name'] != "":
            queryset = queryset.filter(name__icontains = params['name'])
        return queryset

    """ Only admin can create """
    def create(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(PublicCategoriesViewSet, self).create(*args, **kwargs)
        else:
            return Response({'message':'You\'re not authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
    """ user admin can update only his detail """
    def update(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(PublicCategoriesViewSet, self).update(*args, **kwargs)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    """ Only admin can delete sites """
    def destroy(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(PublicCategoriesViewSet, self).destroy(*args, **kwargs)
        else:
            return Response({'message':'Invalid Request'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PrivateCategoriesViewSet(CustomModelViewSet):
    """ All User Categories Management """
    
    queryset = PrivateCategories.objects.all()
    
    parser = {
        'create':PrivateCategoriesCreateSerializer,
        'default':PrivateCategoriesSerializer
    }
   
    filter_fields = ('name',)
    
    def filtering(self, params, queryset, user = None):
        if "name" in params and params['name'] != "":
            queryset = queryset.filter(name__icontains = params['name'])
        queryset = queryset.filter(user = self.request.user)
        return queryset

    def post_save(self, obj, created):
        if created:
            obj.user = self.request.user
            obj.save()
    
    """ Only admin can create """
    def create(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(PrivateCategoriesViewSet, self).create(*args, **kwargs)
        else:
            return Response({'message':'You\'re not authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
    """ user admin can update only his detail """
    def update(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            created_user = PrivateCategories.objects.get(pk = kwargs['pk']).user
            if created_user == self.request.user:
                return super(PrivateCategoriesViewSet, self).update(*args, **kwargs)
            else:
                return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    """ Only admin can delete sites """
    def destroy(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            created_user = PrivateCategories.objects.get(pk = kwargs['pk']).user
            if created_user == self.request.user:
                return super(PrivateCategoriesViewSet, self).destroy(*args, **kwargs)
            else:
                return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FeedMapperViewSet(CustomModelViewSet):
    """ All Feed Mapper Management """
    
    queryset = FeedMapper.objects.all()
    
    parser = {
        'default':FeedMapperSerializer
    }
   
    filter_fields = ('url',)
    
    def post_save(self, obj, created):
        if created:
            feeds = feedparser.parse(obj.feed_url)['entries']
            for post in feeds:
                temp = {}
                temp['feed'] = obj
                temp['feedid'] = post['id']
                titleRef = BeautifulSoup(post['title']).text
                temp['feed_title'] = titleRef
                summaryRef = BeautifulSoup(post['summary']).text
                temp['feed_summary'] = summaryRef
                temp['feed_link'] = post['id']
                if 'content' in post:
                    imgRef = BeautifulSoup(post['content'][0].value)
                    try:
                        if imgRef.find('img').get('src'):
                            temp['feed_image'] = imgRef.find('img')['src']
                    except:
                        pass
                feedRef = Feeds(**temp)
                feedRef.save()



    def filtering(self, params, queryset, user = None):
        if "url" in params and params['url'] != "":
            queryset = queryset.filter(url__icontains = params['url'])
        return queryset
    
    """ Only admin can create """
    def create(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(FeedMapperViewSet, self).create(*args, **kwargs)
        else:
            return Response({'message':'You\'re not authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
    """ user admin can update only his detail """
    def update(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(FeedMapperViewSet, self).update(*args, **kwargs)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    """ Only admin can delete sites """
    def destroy(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(FeedMapperViewSet, self).destroy(*args, **kwargs)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FeedsViewSet(CustomModelViewSet):
    """ All Feed Mapper Management """
    
    queryset = Feeds.objects.all()
    
    parser = {
        'default':FeedsSerializer
    }
   
    filter_fields = ('feed_summary','feedid','feed','feed_link')
    
    def filtering(self, params, queryset, user = None):
        userFeeds = UserSubscriptions.objects.filter(user = self.request.user).values_list('feeds')
        queryset = queryset.filter(feed__in = userFeeds)
        if "feed_summary" in params and params['feed_summary'] != "":
            queryset = queryset.filter(feed_summary__icontains = params['feed_summary'])
        if "feedid" in params and params['feedid'] != "":
            queryset = queryset.filter(feedid__icontains = params['feedid'])
        if "feed" in params and params['feed'] != "":
            queryset = queryset.filter(feed = params['feed'])
        if "feed_link" in params and params['feed_link'] != "":
            queryset = queryset.filter(feed_link__icontains = params['feed_link'])
        queryset = queryset.order_by('-id')
        return queryset
    
    """ Only admin can create """
    def create(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(FeedsViewSet, self).create(*args, **kwargs)
        else:
            return Response({'message':'You\'re not authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
    """ user admin can update only his detail """
    def update(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(FeedsViewSet, self).update(*args, **kwargs)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    """ Only admin can delete sites """
    def destroy(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(FeedsViewSet, self).destroy(*args, **kwargs)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class UserSubscriptionsViewSet(CustomModelViewSet):
    """ All Feed Management """
    
    queryset = UserSubscriptions.objects.all()
    
    parser = {
        'list':UserSubscriptionsListSerializer,
        'retrieve':UserSubscriptionsListSerializer,
        'default':UserSubscriptionsSerializer
    }
   
    filter_fields = ('user',)
    
    def post_save(self, obj, created):
        if created:
            obj.user = self.request.user
            obj.save()


    def filtering(self, params, queryset, user = None):
        queryset = queryset.filter(user = self.request.user)
        if "feeds" in params and params['feeds'] != "":
            queryset = queryset.filter(feeds = int(params['feeds']))
        return queryset
    
    """ Only admin can create """
    def create(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(UserSubscriptionsViewSet, self).create(*args, **kwargs)
        else:
            return Response({'message':'You\'re not authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
    """ user admin can update only his detail """
    def update(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(UserSubscriptionsViewSet, self).update(*args, **kwargs)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # """ Only admin can delete sites """
    # def destroy(self, *args, **kwargs):
    #     return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class FeedStatusViewSet(CustomModelViewSet):
    """ All Feed Management """
    
    queryset = FeedStatus.objects.all()
    
    parser = {
        'default':FeedStatusSerializer
    }
   
    filter_fields = ('status',)
    
    def filtering(self, params, queryset, user = None):
        if "status" in params and params['status'] != "":
            queryset = queryset.filter(status__icontains = params['status'])
        queryset = queryset.filter(user = self.request.user)
        return queryset
    
    """ Only admin can create """
    def create(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(FeedStatusViewSet, self).create(*args, **kwargs)
        else:
            return Response({'message':'You\'re not authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
    """ user admin can update only his detail """
    def update(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(FeedStatusViewSet, self).update(*args, **kwargs)
        else:
            return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    """ Only admin can delete sites """
    def destroy(self, *args, **kwargs):
        return Response({'message':'Youre not Authorized'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
