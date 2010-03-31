from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^logout/$', "account.views.logout" , {}, 'bundestagger-account-logout'),
    (r'^username/$', "account.views.change_username" , {}, 'bundestagger-account-change_username'),
)