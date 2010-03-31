from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', "bundestagger.bundesstats.views.show", {}, 'bundestagger-bundesstats-show'),
)