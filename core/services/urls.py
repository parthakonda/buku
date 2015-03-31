from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^get_feed_url/$', 'core.services.views.getFeedUrl'),
)
