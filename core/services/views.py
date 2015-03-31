from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import View
import feedparser
import json, requests
from bs4 import BeautifulSoup
from .models import FeedMapper
# from BeautifulSoup import BeautifulSoup
import urllib2

FEED_LINKS_ATTRIBUTES = (
    (('type', 'application/rss+xml'),),
    (('type', 'application/atom+xml'),),
    (('type', 'application/rss'),),
    (('type', 'application/atom'),),
    (('type', 'application/rdf+xml'),),
    (('type', 'application/rdf'),),
    (('type', 'text/rss+xml'),),
    (('type', 'text/atom+xml'),),
    (('type', 'text/rss'),),
    (('type', 'text/atom'),),
    (('type', 'text/rdf+xml'),),
    (('type', 'text/rdf'),),
    (('rel', 'alternate'), ('type', 'text/xml')),
    (('rel', 'alternate'), ('type', 'application/xml')),
)
 

def home(request):
    return render_to_response("base.html", {}, context_instance=RequestContext(request))


def extract_feed_links(html, feed_links_attributes=FEED_LINKS_ATTRIBUTES):
    soup = BeautifulSoup(html.content)
    head = soup.find('head')
    links = []
    for attrs in feed_links_attributes:
        for link in head.findAll('link', dict(attrs)):
            href = dict(link.attrs).get('href', '')
            if href: 
                yield unicode(href)
 

def get_first_working_feed_link(url):
    """
        Try to use the current URL as a feed. If it works, returns it.
        It it doesn't, load the HTML and try to get links from it then
        test them one by one and returns the first one that works.

        >>> get_first_working_feed_link('http://www.codinghorror.com/blog/')
        u'http://feeds.feedburner.com/codinghorror/'
        >>> get_first_working_feed_link('http://feeds.feedburner.com/codinghorror/')
        u'http://feeds.feedburner.com/codinghorror/'
    """
 
    # if the url is a feed itself, returns it
    # import pdb;pdb.set_trace()
    html = requests.get(url)
    feed = feedparser.parse(html)
    
    if not feed.get("bozo", 1):
        return unicode(url)
 
    # construct the site url from the domain name and the protocole name    
    parsed_url = urllib2.urlparse.urlparse(url)
    site_url = u"%s://%s" % (parsed_url.scheme, parsed_url.netloc)
    
    # parse the html extracted from the url, and get all the potiential
    # links from it then try them one by one
    for link in extract_feed_links(html):
        if '://' not in link: # if we got a relative URL, make it absolute 
            link = site_url + link
        feed = feedparser.parse(link)
        if not feed.get("bozo", 1):
            return link
 
    return None

def _getFeedUrl(url):
    ourl = url
    
    url = get_first_working_feed_link(url)
    try:
        if url is None:
            if ourl.endswith("/"):
                reqRef = requests.get(ourl+"feed")
                feed = feedparser.parse(reqRef.content)
                if not feed.get("bozo", 1):
                    return ourl+"feed"
                url = get_first_working_feed_link(ourl+"feed")
            else:
                reqRef = requests.get(ourl+"/feed")
                feed = feedparser.parse(reqRef.content)
                if not feed.get("bozo", 1):
                    return ourl+"/feed"
                url = get_first_working_feed_link(ourl+"/feed")
        if url is None:
            if ourl.endswith("/"):
                url = get_first_working_feed_link(ourl+"blog")
            else:
                url = get_first_working_feed_link(ourl+"/blog")
        return url
    except:
        return None

def getFeedUrl(request):
    if request.method == "POST":
        if "url" in request.POST:
            url = request.POST['url']
            ourl = url
            #Look in local
            # import pdb;pdb.set_trace()
            if not ourl.startswith("http://") and not ourl.startswith("http://"):
                url = "http://" + ourl
            if ourl.endswith("/"):
                url = url[:-1]
            fmapRef = FeedMapper.objects.filter(url = url)
            if len(fmapRef) > 0:
                message = "Feed url found"
                return HttpResponse(json.dumps({'message':message, 'url':url,'feedurl':fmapRef[0].feed_url}))
            try:
                rurl = _getFeedUrl(url)
            except:
                rurl = None
                if rurl is None:
                    if not ourl.startswith("http://") and not ourl.startswith("http://"):
                        rurl = "https://" + ourl
                    if ourl.endswith("/"):
                        rurl = url[:-1]
                    fmapRef = FeedMapper.objects.filter(url = rurl)
                    if len(fmapRef) > 0:
                        message = "Feed url found"
                        return HttpResponse(json.dumps({'message':message, 'url':rurl, 'feedurl':fmapRef[0].feed_url}))
                    url = rurl
                    rurl = _getFeedUrl(rurl)
            if rurl is None:
                message = "Feed url not found"
            else:
                message = "Feed url found"
            return HttpResponse(json.dumps({'url':url,'feedurl':rurl, 'message':message}))
        return HttpResponse(json.dumps({'message':"Invalid"}))

def readFeed(request):
    if request.method == "GET":
        return render_to_response("feeds.html", {}, context_instance=RequestContext(request))
    if request.method == "POST":
        if "url" in request.POST:
            url = request.POST['url']
            ourl = url
            url = get_first_working_feed_link(url)
            if url is not None:
                feed = feedparser.parse(url)
            else:
                if ourl.endswith("/"):
                    url = get_first_working_feed_link(ourl+"blog")
                else:
                    url = get_first_working_feed_link(ourl+"/blog")
                if url is not None:
                    feed = feedparser.parse(url)
                else:
                    return HttpResponse("Not Avalable")
            EXCEPT = ['published_parsed', 'published', 'updated', 'updated_parsed']
            posts = []

            if len(feed['entries']) > 0:
                keys = feed['entries'][0].keys()
                print keys
                for post in feed['entries']:
                    temp = {}
                    for key in keys:
                        if key not in EXCEPT:
                            try:
                                temp[key] = post[key]
                            except:
                                temp[key] = "NA"
                    posts.append(temp)
        return HttpResponse(json.dumps({'feeds':posts}))



def if_partial_url(url):
    partial_urls = []
    proceed = False
    for purl in partial_urls:
        if url.startswith(purl):
            proceed = True
    return proceed

def CatchAllUrl(request):
    purl = if_partial_url(request.path)
    if purl:
        if not request.user_agent.is_bot:
            return render_to_response('base.html', {}, context_instance=RequestContext(request))
    else:
        return HttpResponse("Page Not Found")