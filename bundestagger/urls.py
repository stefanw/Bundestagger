from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template

from bundestagger.account.openid_consumer import BundesOpenidConsumer
from bundestagger.helper.utils import is_get

# direct to template may only be GET requests (post may be evil, caching wise)
direct_to_template = is_get(direct_to_template)

admin.autodiscover()

openid_consumer = BundesOpenidConsumer()

urlpatterns = patterns('',
    (r'^$', direct_to_template, {"template": "index.html"}, "bundestagger-index"), 
    (r'^impressum/$', direct_to_template, {"template": "impressum.html"}, "bundestagger-impressum"),
    (r'^informationen/$', direct_to_template, {"template": "informationen.html"}, "bundestagger-informationen"),
    (r'^api/$', direct_to_template, {"template": "api.html"}, "bundestagger-api"),
    (r'^nutzungsbedingungen-datenschutz/$', direct_to_template, {"template": "terms.html"}, "bundestagger-terms"),
    (r'^webtv/config/(?P<id>\d+)/$', direct_to_template, {"template": "bundestag/config.xml"}, "bundestagger-webtvconfig"),
    (r'^api/', include('bundestagger.api.urls')),
    (r'^bundesadmin/', include(admin.site.urls)),
    (r'^annotate/', include('annotatetext.urls')),
    (r'^improvement/', include('improvetext.urls')),
    (r'^search/', include('bundestagger.search.urls')),
    (r'^user/', include('bundestagger.account.urls')),
    (r'^tag/', include('bundestagger.bundestagging.urls')),
    (r'^statistiken/', include('bundestagger.bundesstats.urls')),
    (r'^openid/', include(openid_consumer.urls)),
    (r'^', include('bundestagger.bundestag.urls')),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
    (r'^(?P<path>crossdomain\.xml)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
