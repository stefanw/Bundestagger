# -*- coding: utf-8 -*-
import re

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.template import RequestContext
from django.utils.itercompat import groupby
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.conf import settings
from django.db.models import Q

from improvetext.models import Improvement

from models import ParliamentSession, Speech, SpeechPart, Event, Politician
from forms import EditSpeechPartForm
from bundestagger.account.auth import logged_in
from bundestagger.helper.utils import invalidate_cache, is_post, is_get


@is_get
def list_sessions(request):
    sessions = ParliamentSession.objects.select_related("parliament").order_by("-parliament__number", "-number")
    parliaments = groupby(sessions, lambda s: s.parliament)
    new_parliaments = []
    for parliament, it in parliaments:
        parliament.sessions = list(it)
        new_parliaments.append(parliament)
    return render_to_response("bundestag/list_sessions.html", RequestContext(request, {"parliaments" : new_parliaments}))

@is_get
def show_session(request, parliament_nr, session_nr):
    def find(func, it):
        for i in it:
            if func(i):
                return i
        return None
    content = u""
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        parliament_session = ParliamentSession.objects.select_related("parliament").get(number=int(session_nr), parliament__number=int(parliament_nr))
    except ParliamentSession.DoesNotExist:
        raise Http404
#    sessiontops = SessionTop.objects.get_tops(parliament_session)
#    sessiontopids = [st.id for st in sessiontops]
#    topspeakers = TopSpeaker.objects.filter(top__id__in=sessiontopids)
#    for sessiontop in sessiontops:
#        sessiontop.topspeakers = []
#        sessiontop.topspeaker_ids = []
#    for topspeaker in topspeakers:
#        sessiontop = find(lambda x: x.id == topspeaker.top_id, sessiontops)
#        sessiontop.topspeaker_ids.append(topspeaker.speaker_id)
#    topoffset = 0
#    topspeakeroffset = 0
#    for speech in Speech.objects.filter(session=parliament_session).order_by("ordernr"):
#        for sessiontop in sessiontops:
#            if speech.speaker_id in sessiontop.topspeaker_ids:
#                sessiontop.topspeaker_ids.remove(speech.speaker_id)
#                sessiontop.topspeakers.append(speech)
#                break
    all_speeches = Speech.objects.select_related("speaker", "speaker__party","session","session__parliament")\
        .filter(session=parliament_session).order_by("ordernr")
    paginator = Paginator(all_speeches, settings.SPEECHES_PER_PAGE)
    try:
        page_obj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_obj = paginator.page(paginator.num_pages)
    gt = ((page - 1) * settings.SPEECHES_PER_PAGE)
    lte = (page * settings.SPEECHES_PER_PAGE)
    speech_parts = SpeechPart.objects.filter(speech__session=parliament_session)\
        .filter(speech__ordernr__gt=gt, speech__ordernr__lte=lte)\
        .order_by("speech__ordernr", "ordernr")\
        .select_related("speech", "speech__speaker", "speech__speaker__party")
    speeches = groupby(speech_parts, lambda sp: sp.speech)
    new_speeches = []
    for speech, it in speeches:
        speech.speech_parts = list(it)
        new_speeches.append(speech)
    events = Event.objects.filter(context__id__in=[speech_part.id for speech_part in speech_parts])\
        .select_related("context", "actor_politician", "actor_party")
    events = groupby(events, lambda e: e.context.id)
    new_events = {}
    for k,v in events:
        new_events[k] = list(v)
    return render_to_response("bundestag/show.html", RequestContext(request, {"session" : parliament_session, 
        "speech_parts": speech_parts,
        "speeches": new_speeches, 
        "events": new_events,
        "paginator": paginator,
        "page_obj":page_obj,
#        "sessiontops":sessiontops
        "all_speeches": all_speeches
        }))

@is_post
@logged_in
def edit_speechpart(request, speechpart_id):
    try:
        speech_part = SpeechPart.objects.select_related("speech").get(id=int(speechpart_id))
    except SpeechPart.DoesNotExist:
        raise Http404
    edit_form = EditSpeechPartForm(request.POST)
    if edit_form.is_valid():
        if request.bundesuser.is_moderator:
            speech_part.set_text(edit_form.cleaned_data["text"])
            messages.add_message(request, messages.INFO, u"Änderung gespeichert")
        else:
            Improvement.objects.suggest(obj=speech_part, user=request.bundesuser, field="text", change=edit_form.cleaned_data["text"])
            messages.add_message(request, messages.INFO, u"Änderung wurde vorgeschlagen, ist aber noch nicht sichtbar!")
    return redirect(speech_part.speech.get_absolute_url())

@is_post
def add_webtvurl(request):
    if "speech_id" not in request.POST:
        return HttpResponseBadRequest()
    try:
        speech_id = int(request.POST["speech_id"])
    except TypeError:
        return HttpResponseBadRequest()
    try:
        speech = Speech.objects.get(id=speech_id)
    except SpeechPart.DoesNotExist:
        raise Http404
    if "url" not in request.POST:
        return HttpResponseBadRequest()
    webtvurl = request.POST["url"]
#    http://webtv.bundestag.de/iptv/player/macros/_v_f_514_de/od_player.html?singleton=true&content=168834
    match = re.match("^http://webtv\.bundestag\.de/.*?content=([0-9]+)$", webtvurl)
    if match is None:
        messages.add_message(request, messages.INFO, u"Ungültige Bundestags-WebTV-URL!")
        return HttpResponseBadRequest()
    else:
        webtvid = int(match.group(1))
        speech.webtv = webtvid
        speech.save()
        speech.clear_cache()
        messages.add_message(request, messages.INFO, u"Bundestags-WebTV-URL gespeichert!")
    return redirect(speech.get_absolute_url())
    
def show_politician(request, slug, pid):
    try:
        politician = Politician.objects.get(id=int(pid))
    except Politician.DoesNotExist:
        raise Http404
    if politician.slug != slug:
        return redirect(politician.get_absolute_url())
    speeches = Speech.objects.select_related("session", "session__parliament").filter(speaker=politician).order_by("-session__parliament__number", "-session__number", "ordernr")
    eventcount = Event.objects.filter(actor_politician=politician).count()
    everything = politician.all_relations()
    return render_to_response("bundestag/show_politician.html", RequestContext(request, {
        "politician": politician, 
        "speeches" : speeches, 
        "eventcount":eventcount,
        "everything": everything
    }))
