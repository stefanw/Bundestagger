from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.template import RequestContext
from django.conf import settings
from django.utils import simplejson

from bundestagger.helper.utils import is_get

import urllib, urllib2

YBOSS_URL = "http://boss.yahooapis.com/ysearch/%(vertical)s/v1/%(query)s?appid=%(appkey)s&start=%(start)d&region=de&lang=de&style=raw&sites=bundestagger.de&format=json"

@is_get
def search(request):
    if not "q" in request.GET:
        return HttpResponseBadRequest()
    query = request.GET["q"]
    page = 0
    if "page" in request.GET:
        try:
            page = int(request.GET["page"])
        except TypeError:
            pass
    try:
        response = urllib2.urlopen(YBOSS_URL % {"vertical": "web", "query":query, "appkey":settings.YAHOO_BOSS_KEY, "start": page})
    except (urllib2.HTTPError,urllib2.URLError):
        return HttpResponseBadRequest()
    result = simplejson.loads(response.read())
    return render_to_response("search/results.html", RequestContext(request, {"searchresult" : result["ysearchresponse"]}))