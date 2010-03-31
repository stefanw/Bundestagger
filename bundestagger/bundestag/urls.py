from django.conf.urls.defaults import *
from feeds import LatestSessionsFeed, LatestSessionsFeedAtom

urlpatterns = patterns('',
    (r'^sitzungen/rss/$', LatestSessionsFeed(), {}, "bundestagger-session-rss"),
    (r'^sitzungen/atom/$', LatestSessionsFeedAtom(), {}, "bundestagger-session-atom"),
    (r'^sitzungen/$', "bundestag.views.list_sessions" , {}, 'bundestagger-bundestag-list_sessions'),
    (r'^revise/(\d+)/$', "bundestag.views.edit_speechpart" , {}, 'bundestagger-bundestag-edit_speechpart'),
    (r'^webtv/add/$', "bundestag.views.add_webtvurl" , {}, 'bundestagger-bundestag-add_webtvurl'),
    (r'^(\d+)/sitzung/(\d+)/$', "bundestag.views.show_session" , {}, 'bundestagger-bundestag-show_session'),
#    (r'^fix_politicians/$', "bundestag.views.fix_politicians" , {}, 'bundestagger-bundestag-fix_politicians'),
#    (r'^import_wiki/$', "bundestag.views.import_members_wikipedia" , {}, 'bundestagger-bundestag-import_members_wikipedia'),
#    (r'^([\w-]+)/(\d+)$', "bundestag.views.show_politician" , {}, 'bundestagger-bundestag-show_politician'),
    
    
#    (r'^(\d+)/ordertops/(\d+)/$', "bundestag.views.order_tops" , {}, 'bundestagger-bundestag-order_tops'),
)