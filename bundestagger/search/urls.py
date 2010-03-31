from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', "search.views.search" , {}, 'bundestagger-search'),
)