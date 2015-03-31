from django.conf.urls import patterns, include, url
from django.contrib import admin
from core.authentication.viewsets import UsersViewSet
from rest_framework.routers import DefaultRouter
from core.services.viewsets import PublicCategoriesViewSet, PrivateCategoriesViewSet, FeedMapperViewSet, FeedsViewSet, FeedStatusViewSet, UserSubscriptionsViewSet

router = DefaultRouter()

router.register(r'profile', UsersViewSet)
router.register(r'categories', PublicCategoriesViewSet)
router.register(r'usercategories', PrivateCategoriesViewSet)
router.register(r'feedmapper', FeedMapperViewSet)
router.register(r'feeds', FeedsViewSet)
router.register(r'feedstatus', FeedStatusViewSet)
router.register(r'usersubscriptions', UserSubscriptionsViewSet)


urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^$', 'core.services.views.home'),
    url(r'^readfeed/$', 'core.services.views.readFeed'),
    url(r'^', include('core.authentication.urls')),
    url(r'^', include('core.services.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
