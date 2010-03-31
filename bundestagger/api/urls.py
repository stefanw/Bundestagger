from django.conf.urls.defaults import *
from piston.resource import Resource

from bundestagger.api.views import documentation_view
from bundestagger.api.handlers import ParliamentHandler, ParliamentSessionHandler, TagHandler, SpeechHandler

parliaments = Resource(handler=ParliamentHandler)
parliamentsessions = Resource(handler=ParliamentSessionHandler)
tags = Resource(handler=TagHandler)
speeches = Resource(handler=SpeechHandler)

urlpatterns = patterns('',
    url(r'^parliaments$', parliaments, name='api-parliaments'),
    url(r'^parliaments\.(?P<emitter_format>(?:json|xml))$', parliaments, name='api-parliaments'),
    url(r'^parliament/(?P<parliament_number>\d+)$', parliaments, name='api-parliament'),
    url(r'^parliament/(?P<parliament_number>\d+)\.(?P<emitter_format>(?:json|xml))$', parliaments, name='api-parliament'),

    url(r'^sessions/(?P<parliament_number>\d+)$', parliamentsessions, name='api-parliamentsessions'),    
    url(r'^sessions/(?P<parliament_number>\d+)\.(?P<emitter_format>(?:json|xml))$', parliamentsessions, name='api-parliamentsessions'),
    url(r'^session/(?P<parliament_number>\d+)/(?P<session_number>\d+)$', parliamentsessions, name='api-parliamentsession'),    
    url(r'^session/(?P<parliament_number>\d+)/(?P<session_number>\d+)\.(?P<emitter_format>(?:json|xml))$', parliamentsessions, name='api-parliamentsession'),

    url(r'^tags$', tags, name='api-tags'),    
    url(r'^tags\.(?P<emitter_format>(?:json|xml))$', tags, name='api-tags'),
    url(r'^tag/(?P<tag>(?:json|xml)?)\.(?P<emitter_format>(?:json|xml))$', tags, name='api-tag'),
    url(r'^tag/(?P<tag>(?:json|xml))$', tags, name='api-tag'),

    url(r'^speeches/(?P<parliament_number>\d+)/(?P<session_number>\d+)$', speeches , name='api-speeches'),    
    url(r'^speeches/(?P<parliament_number>\d+)/(?P<session_number>\d+)\.(?P<emitter_format>(?:json|xml))$', speeches, name='api-speeches'),
    url(r'^speech/(?P<speech_id>\d+)$', speeches, name='api-speech'),
    url(r'^speech/(?P<speech_id>\d+)\.(?P<emitter_format>(?:json|xml))$', speeches, name='api-speech'),
#    url(r'^speech/random$', speeches, name='api-speech-random'),
#    url(r'^speech/random\.(?P<emitter_format>(?:json|xml))$', speeches, name='api-speech-random'),


    # automated documentation
#    url(r'^documentation/$', documentation_view),
)