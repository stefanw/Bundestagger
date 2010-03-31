"""
Tagging related views.
"""
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext, loader, Context

from tagging.models import Tag, TaggedItem
from tagging.utils import parse_tag_input, get_tag, get_queryset_and_model


def add_tags(request, content_type=None, object_id=None, ajax=False):
    if request.method=="POST":
        content_type = get_object_or_404(ContentType, id = int(content_type))
        tagged_object = content_type.get_object_for_this_type(id = int(object_id))
        if not hasattr(tagged_object,"tags"):
            return HttpResponseBadRequest()
        li = tagged_object.tags.split(",")
        s = set([l.strip() for l in li if len(l.strip())>0])
        new_tags = parse_tag_input(request.POST["tags"])
        s.update(new_tags)
        tagged_object.tags = ",".join(s)
        tagged_object.save()
        tagged_object.clear_cache()
        if request.is_ajax():
            t = loader.get_template("tagging/_tag_list.html")
            return HttpResponse(t.render(RequestContext(request, {"tags": new_tags})))
            
        else:
            next = "/"
            if "next" in request.POST:
                next = request.POST["next"]
            else:
                next = tagged_object.get_absolute_url()
            return HttpResponseRedirect(next)

def autocomplete(request):
    q = request.GET.get("q","")
    try:
        limit = int(request.GET.get("limit",10))
    except TypeError:
        limit = 10
    return HttpResponse("\n".join(map(lambda x:x.name,Tag.objects.filter(name__istartswith=q)[:limit])),mimetype="text/plain")