# -*- coding: utf-8 -*-
import datetime
from difflib import SequenceMatcher
import re

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.urlresolvers import reverse
from django.conf import settings
import django.dispatch
from django.template.defaultfilters import slugify

from tagging.fields import TagField

from bundestagger.helper.utils import padd_zeros, invalidate_cache, invalidate_cache_all_pages, get_page


FRAKTIONEN = (u"fraktionslos", u"CDU/CSU", u"BÜNDNIS 90/DIE GRÜNEN", u"FDP", u"SPD", u"DIE LINKE")

class PartyManager(models.Manager):
    
    cache = {}
    
    def get_party(self, name="", abbr=None):
        if abbr is None:
            return None
        if abbr not in FRAKTIONEN:
            if u"INKE" in abbr:
                abbr = u"DIE LINKE"
            if u"CDU" in abbr or u"CSU" in abbr:
                abbr = u"CDU/CSU"
            if u"NDNIS" in abbr:
                abbr = u"BÜNDNIS 90/DIE GRÜNEN"
            if u"raktionslos" in abbr:
                abbr = u"fraktionslos"
        if abbr in FRAKTIONEN:
            try:
                party = self.get(abbr=abbr)
            except self.model.DoesNotExist:
                party = self.create(name=name, abbr=abbr)
            return party
        return None
        
    def find_parties_in_text(self, text, force=False):
        abbrs = []
        if u"INKE" in text and (not u"INKE]" in text or force):
            abbrs.append(u"DIE LINKE")
        if u"CDU" in text and (not u"[CDU" in text or force) or \
            (u"CSU" in text and (not u"CSU]" in text or force)):
            abbrs.append(u"CDU/CSU")
        if u"NDNIS" in text and (not u"ÜNEN]" in text or force):
            abbrs.append(u"BÜNDNIS 90/DIE GRÜNEN")
        if u"raktionslos" in text and (not u"raktionslos]" in text or force):
            abbrs.append(u"fraktionslos")
        if u"SPD" in text and (not u"[SPD]" in text or force):
            abbrs.append(u"SPD")
        if u"FDP" in text and (not u"[FDP]" in text or force):
            abbrs.append(u"FDP")
        parties = []
        for abbr in abbrs:
            parties.append(self.get_party(abbr=abbr))
        return parties
        
    def get(self, *args, **kwargs):
        if "id" in kwargs:
            if kwargs["id"] in self.__class__.cache:
                return self.__class__.cache[kwargs["id"]]
            else:
                obj = super(PartyManager, self).get_query_set().get(*args, **kwargs)
                self.__class__.cache[obj.id] = obj
                return obj
        return super(PartyManager, self).get_query_set().get(*args, **kwargs)


    
class Party(models.Model):
    name = models.CharField(blank=True, max_length=100)
    abbr = models.CharField(blank=True, max_length=30)
    
    objects = PartyManager()
    
    color_mapping = {
        1 : "#000000",
        2 : "#F1AB00",
        3 : "#D71F1D",
        4 : "#BE3075",
        5 : "#78BC1B",
        6 : "#999999"
    }
    
    def __unicode__(self):
        return self.abbr

    @property
    def color(self):
        return self.color_mapping[self.id]
        
class PoliticianManager(models.Manager):
            
    def replace_politician(self, real, fake):
        real = Politician.objects.get(id=real)
        fake = Politician.objects.get(id=fake)
        fake.replace_with(real)
        fake.delete()
    
class Politician(models.Model):
    first_name = models.CharField(blank=True, max_length=100)
    last_name_prefix = models.CharField(blank=True, max_length=100)
    last_name = models.CharField(blank=True, max_length=100)
    title = models.CharField(blank=True, max_length=100)
    party = models.ForeignKey(Party, blank=True, null=True)
#    party_member = models.OneToOneField(PartyMember, blank=True, null=True)
    location = models.CharField(null=True, blank=True, max_length=255)
    born = models.DateField(null=True, blank=True)
    
    objects = PoliticianManager()

    def __unicode__(self):
        if self.party_id is not None:
            party = Party.objects.get(id=self.party_id)
            return u"%s (%s)" % (self.name, party)
        else:
            return u"%s (unbekannt)" % (self.name)

    @property
    def slug(self):
        return slugify(self.name)

    def get_absolute_url(self):
        return reverse("bundestagger-bundestag-show_politician", args=(self.slug, self.id))

    @property    
    def name(self):
        if len(self.title):
            title = self.title + u" "
        else:
            title= u""
        if len(self.first_name):
            first_name = self.first_name + u" "
        else:
            first_name = u""
        if len(self.last_name_prefix):
            last_name_prefix = self.last_name_prefix + u" "
        else:
            last_name_prefix = u""
        return "%s%s%s%s" % (title, first_name, last_name_prefix,self.last_name)
        
    def all_relations(self):
        relations = [x for x in dir(self) if x.endswith("_set")]
        result = []
        for relation in relations:
            result.extend(getattr(self, relation).all())
        return result
        
    def replace_with(self, real_politician):
        relations = [x for x in dir(self) if x.endswith("_set")]
        for relation in relations:
            relset = getattr(self, relation).all()
            if len(relset) > 0:
                politician_fields = []
                for obj in relset:
                    fields = obj.__class__._meta.fields
                    for field in fields:
                        try:
                            if field.rel.to.__name__ == self.__class__.__name__:
                                politician_fields.append(field.name)
                        except AttributeError:
                            pass
                    if len(politician_fields)>0:
                        for pf in politician_fields:
                            if getattr(obj, pf) == self:
                                setattr(obj, pf, real_politician)
                                obj.save()
                                    
class Parliament(models.Model):
    number = models.IntegerField()
    start = models.DateField(default=datetime.datetime.today, null=True, blank=True)
    end = models.DateField(default=datetime.datetime.today, null=True, blank=True)
    
    def __unicode__(self):
        return u"Parliament %d" % (self.number,)
        
class MemberOfParliament(models.Model):
    politician = models.ForeignKey(Politician)
    parliament = models.ForeignKey(Parliament)
    position = models.CharField(null=True, blank=True, max_length=255)
    location = models.CharField(blank=True, max_length=100)
    direct = models.FloatField(null=True, blank=True, default=None)
    
    class Meta:
        unique_together = (("politician", "parliament"),)
        
    def __unicode__(self):
        return "%s (%s)" % (self.politician, self.parliament)

        
class ParliamentSessionManager(models.Manager):
    def reversed(self):
        return self.order_by("-number")

    def ordered(self):
        return self.order_by("number")
    
class ParliamentSession(models.Model):
    parliament = models.ForeignKey(Parliament)
    number = models.PositiveSmallIntegerField(db_index=True)
    date = models.DateTimeField()
    until = models.DateTimeField()
    checked = models.BooleanField(default=False)
    
    tags = models.TextField(blank=True)
    
    objects = ParliamentSessionManager()
    
    def __unicode__(self):
        return u"%d. Sitzung  (%s) des %d. Deutschen Bundestags" % (self.number, self.date.strftime("%d.%m.%Y"), self.parliament.number)
        
    def get_absolute_url(self):
        return reverse("bundestagger-bundestag-show_session", args=(self.parliament.number, self.number))
        
    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(",") if len(tag.strip())>0]
        
    def update_tags(self,new_tags):
        tag_set = set([t.strip() for t in self.tags.split(",") if len(t.strip())>0])
        tag_set.update([t.strip() for t in new_tags.split(",") if len(t.strip())>0])
        self.tags = ",".join(tag_set)
        self.clear_cache()
        self.save()
    
    @property
    def document_url(self):
        return "http://dip21.bundestag.de/dip21/btp/%(leg)d/%(leg)d%(id)s.pdf" % {"leg":self.parliament.number, "id": padd_zeros(self.number)}
    
    def clear_cache(self):
        invalidate_cache(reverse("bundestagger-bundestag-list_sessions"))
        last_speech = self.speech_set.order_by("-ordernr")[0]
        url = last_speech.get_base_url()
        invalidate_cache_all_pages(url, last_speech.ordernr, settings.SPEECHES_PER_PAGE)

class SpeechManager(models.Manager):
    def merge(self):
        for speech in self.all():
            ordernr = 1
            previous_parts = []
            for speech_part in speech.speechpart_set.all():
                if len(previous_parts) > 1 and \
                    (speech_part.speaker != previous_parts[-1].speaker or previous_parts[-1].event_set.count() > 0):
                    text = u""
                    for p in previous_parts:
                        text += p.text
                    previous_parts[-1].text = text
                    previous_parts[-1].ordernr = ordernr
                    previous_parts[-1].save()
                    for p in previous_parts[:-1]:
                        p.delete()
                    previous_parts = []
                
                
    
class Speech(models.Model):
    session = models.ForeignKey(ParliamentSession)
    ordernr = models.IntegerField()
    speaker = models.ForeignKey(Politician)
    start = models.DateTimeField(blank=True, default=None, null=True)
    end = models.DateTimeField(blank=True, default=None, null=True)
    webtv = models.IntegerField(blank=True, null=True)
    
    tags = TagField(blank=True)
    
    def save(self, *args, **kwargs):
        super(Speech,self).save(*args, **kwargs)
        self.session.update_tags(self.tags)
        
    
    def __unicode__(self):
        return u"Rede von %s in der %s" % (self.speaker, self.session)
        
    def text(self):
        return u"\n".join(map(lambda x:x.text, self.speechpart_set.order_by("ordernr")))
        
    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(",") if len(tag.strip())>0]
    
    @property
    def webtv_url(self):
        if self.webtv is not None:
            return u"http://webtv.bundestag.de/iptv/player/macros/_v_f_514_de/od_player.html?singleton=true&content=%d" % (self.webtv,)
        return u""
    
    @property
    def webtv_search(self):
        url = u"http://webtv.bundestag.de/iptv/player/macros/bttv/list.html?pageOffset=0&pageLength=40&sort=2&lastName=%(lastname)s&firstName=%(firstname)s&fraction=&meetingNumber=%(session)s&period=%(period)s&startDay=&endDay=&topic=&submit=Suchen"
        return url % {  "firstname": self.speaker.first_name, 
                        "lastname": self.speaker.last_name,
                        "session": self.session.number,
                        "period": self.session.parliament.number
                        }
    
    def get_base_url(self):
        return reverse("bundestagger-bundestag-show_session", args=(self.session.parliament.number, self.session.number))
        
    def get_absolute_url(self):
        page = get_page(self.ordernr, settings.SPEECHES_PER_PAGE)
        if page == 1:
            page = ""
        else:
            page = "?page=%d" % page
        fragment = "#speech-%d" % self.id
        return self.get_base_url() + page + fragment

    def clear_cache(self):
        url = self.get_base_url()
        invalidate_cache(url, self.ordernr, settings.SPEECHES_PER_PAGE)
        
class SpeechPartManager(models.Manager):
    def list(self):
        return self.order_by("ordernr").select_related()
    
class SpeechPart(models.Model):
    speech = models.ForeignKey(Speech)
    ordernr = models.IntegerField()
    text = models.TextField(blank=True)
    
    objects = SpeechPartManager()
    
    changed_signal = django.dispatch.Signal(providing_args=["old_text", "new_text"])
    
    annotatable = True
    
    def __unicode__(self):
        return u"Teil %d der %s" % (self.ordernr, self.speech)
    
    def append_text(self, text):
        text = text.strip()
        if self.text == u"":
            self.text = text
        else:
            if self.text.endswith("-"):
                self.text = self.text[:-1] + text
            else:
                self.text = self.text+ " " + text
        self.save()
        return self.text
        
    def set_text(self, text):
        old_text = self.text
        self.text = text
        self.save()
        if hasattr(self.__class__, "changed_signal"):
            self.__class__.changed_signal.send(sender=self, old_text=old_text, new_text=self.text)
        self.clear_cache()
        
        
    def get_absolute_url(self):
        if self.ordernr == 1:
            return self.speech.get_absolute_url()
        else:
            return self.speech.get_absolute_url()+"-%d" % self.ordernr
        
    def clear_cache(self):
        self.speech.clear_cache()
    
    @classmethod
    def connected_update(cls, sender, **kwargs):
        co = kwargs["content_object"]
        co.clear_cache()

class SessionTopManager(models.Manager):
    def get_tops(self, session):
        return self.filter(session=session).filter(Q(title__startswith="Tagesordnungspunkt")|Q(title__startswith="Zusatztagesordnungspunkt")).order_by("ordernr")
        
        
class SessionTop(models.Model):
    session = models.ForeignKey(ParliamentSession)
    ordernr = models.IntegerField()
    title = models.TextField(blank=True)
    about = models.TextField(blank=True)
    
    objects = SessionTopManager()
    
    def __unicode__(self):
        return u"%s: %s" % (self.session, self.title)
    
class TopSpeaker(models.Model):
    top = models.ForeignKey(SessionTop)
    speaker = models.ForeignKey(Politician)

    def __unicode__(self):
        return u"%s: %s(%s) - %s" % (self.speaker, self.top, self.top_id, self.id)
    
class Attachment(models.Model):
    session = models.ForeignKey(ParliamentSession)
    attachmentnr = models.IntegerField(blank=True, null=True)
    about = models.TextField(blank=True)
    text = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s: %s" % (self.session, self.about)
    
class Poll(models.Model):
    session = models.ForeignKey(ParliamentSession)
    about = models.TextField(blank=True)
    infavor = models.IntegerField(blank=True, null=True)
    against = models.IntegerField(blank=True, null=True)
    abstinent = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return u"%s: %s(%s)" % (self.session, self.about[:10], self.id)
    
class PollVote(models.Model):
    # Ja = 1, Nein = 0, Enthalung = -1 oder 2!?
    poll = models.ForeignKey(Poll)
    vote = models.SmallIntegerField()
    politician = models.ForeignKey(Politician)
    
    def __unicode__(self):
        return u"%s: %s (%s - %d)" % (self.poll, self.politician, self.poll_id, self.vote)

class Event(models.Model):
    # Zwischenruf, Buhruf, Heiterkeit, Beifall
    context = models.ForeignKey(SpeechPart, null=True, blank=True)
    kind = models.CharField(blank=True, max_length=100)
    actor_politician = models.ForeignKey(Politician, null=True, blank=True)
    actor_party = models.ForeignKey(Party, null=True, blank=True)    
    text = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u"%s: %s (%s - %s @ %s)" % (self.kind, self.actor, self.text, self.id, self.context_id)
    
    @property
    def actor(self):
        if self.actor_politician is not None:
            return self.actor_politician
        else:
             return self.actor_party

    def display(self):
        out = u""
        try:
            if self.kind != "":
                out+=u"[%s] " % self.kind
            if self.actor is not None:
                out+=u"%s" % self.actor
            if self.text is not None and len(self.text)>0:
                if self.actor is not None or self.kind !="":
                    out+=": "
                out+=self.text
        except Exception,e:
            return e
        return out