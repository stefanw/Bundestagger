from django.conf.urls.defaults import *
from bundestagger.bundestagging.views import add_tags, autocomplete
from bundestagger.bundestag.models import Speech

urlpatterns = patterns('',
    url(r'^add/(?P<content_type>\d+)/(?P<object_id>\d+)/$', add_tags, name='tagging_add-tags'),
    url(r'^autocomplete/$', autocomplete, name='tagging_autocomplete'),
)

urlpatterns += patterns('',
    ('^(?P<tag>[^/]+)$', 'tagging.views.tagged_object_list', {'queryset_or_model': Speech, 'template_name': "bundestagging/tag.html"}, 'tagging-tag_url'),
    )