from django.core.urlresolvers import reverse
from django.http import Http404
from django.conf import settings

from piston.handler import BaseHandler
from piston.decorator import decorator
from tagging.models import Tag, TaggedItem

from bundestagger.bundestag.models import Parliament, ParliamentSession, Speech


THROTTLE_PARAMS = [10, 60, 'user_reads']

def throttle(*args, **kwargs):
    @decorator
    def inner_func(func, *inner_args, **inner_kwargs):
        return func(*inner_args, **inner_kwargs)
    return inner_func

def fullurl(url):
    return settings.SITE_DOMAIN + url

class ParliamentHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(*THROTTLE_PARAMS)   
    def read(self, request, parliament_number=None):
        if parliament_number is None:
            return [{"href": self.get_url(p)} for p in Parliament.objects.all()]
        else:
            try:
                p = Parliament.objects.get(number=int(parliament_number))
            except Parliament.DoesNotExist:
                raise Http404
            return {"number": p.number, "self": self.get_url(p), "start": p.start, "end": p.end,
                "sessions": fullurl(reverse("api-parliamentsessions", kwargs={"parliament_number":p.number}))}
            
    def get_url(self, obj):
        return fullurl(reverse("api-parliament", kwargs={"parliament_number":obj.number}))
        
class ParliamentSessionHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(*THROTTLE_PARAMS)
    def read(self, request, parliament_number=None, session_number=None):
        if session_number is None:
            sessions = ParliamentSession.objects.select_related("parliament").filter(parliament__number=int(parliament_number)).order_by("number")
            return [{"href": self.get_url(s)} for s in sessions]
        else:
            try:
                s = ParliamentSession.objects.select_related("parliament").get(number=int(session_number),parliament__number=int(parliament_number))
            except ParliamentSession.DoesNotExist:
                raise Http404
            return {"number": s.number, "self": self.get_url(s), "date": s.date, "until": s.until, 
                "tags": [{"name": t, "href": fullurl(reverse("api-tag", kwargs={"tag": t})), "url": fullurl(reverse("tagging-tag_url", kwargs={"tag": t}))} for t in s.tag_list],
                "url": fullurl(s.get_absolute_url()),
                "original_document": s.document_url}
            
    def get_url(self, obj):
        return fullurl(reverse("api-parliamentsession", kwargs={"parliament_number":obj.parliament.number,
                    "session_number": obj.number}))

class SpeechHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(*THROTTLE_PARAMS)
    def read(self, request, parliament_number=None, session_number=None, speech_id=None):
        if parliament_number is not None and session_number is not None and speech_id is None:
            speeches = Speech.objects.select_related("session", "session__parliament").filter(session__number=int(session_number), session__parliament__number=int(parliament_number)).order_by("ordernr")
            return [{"href": self.get_url(s)} for s in speeches]
        else:
            if  speech_id is not None:
                try:
                    speech = Speech.objects.select_related("speaker", "speaker__party").get(id=int(speech_id))
                except Speech.DoesNotExist:
                    raise Http404
            else:
                raise Http404
                from random import randint
                count = Speech.objects.all().count()
                speech = Speech.objects.select_related("speaker", "speaker__party").all()[randint(0,count-1)]
                
            fulltext = []
            text = []
            for speech_part in speech.speechpart_set.order_by("ordernr"):
                fulltext.append(speech_part.text)
                text.append({"type":"text", "content": speech_part.text, "url": fullurl(speech_part.get_absolute_url())})
                events = []
                for event in speech_part.event_set.all():
                    event_dict = {"kind": event.kind}
                    if event.text is not None and len(event.text)>0:
                        event_dict["text"] = event.text
                    if event.actor_party is not None:
                        event_dict["actor"] = {"type": "Party", "name": unicode(event.actor)}
                    elif event.actor_politician is not None:
                        event_dict["actor"] = {"type": "Politician", "name": unicode(event.actor)}
                    events.append(event_dict)
                if len(events):
                    text.append({"type": "eventlist", "content": events})
            fulltext = "\n".join(fulltext)
            return {"number": speech.ordernr, "self": self.get_url(speech), "url": fullurl(speech.get_absolute_url()),
                "tags": [{"name": t, "href": fullurl(reverse("api-tag", kwargs={"tag": t})), 
                    "url": fullurl(reverse("tagging-tag_url", kwargs={"tag": t}))} for t in speech.tag_list],
                "speaker": {"fullname": speech.speaker.name, "party": unicode(speech.speaker.party)},
                "text": fulltext,
                "text_with_events": text,
                "original_document": speech.session.document_url,
                "video_url": speech.webtv_url,
                "start": speech.start,
                "end": speech.end}

    def get_url(self, obj):
        return fullurl(reverse("api-speech", kwargs={"speech_id": obj.id}))

                    
class TagHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(*THROTTLE_PARAMS)
    def read(self, request, tag=None):
        if tag is None:
            tags = Tag.objects.all()
            return [{"href": self.get_url(t)} for t in tags]
        else:
            try:
                tag = Tag.objects.get(name=tag)
                related = TaggedItem.objects.get_by_model(Speech, tag)
            except Tag.DoesNotExist:
                raise Http404
            return {"tag": tag.name, "self": self.get_url(tag), "url": fullurl(reverse("tagging-tag_url", kwargs={"tag": tag.name})),
                "related": [{"name": unicode(r), "href": fullurl(reverse("api-speech", kwargs={"speech_id": r.id})), "type": "Speech"} for r in related]}

    def get_url(self, obj):
        return fullurl(reverse("api-tag", kwargs={"tag":obj.name}))