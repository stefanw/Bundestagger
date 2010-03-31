from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.template import RequestContext, loader, Context
from django.utils.itercompat import groupby
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.conf import settings

from bundestagger.bundesstats.models import *
from bundestagger.helper.utils import invalidate_cache, is_get

@is_get
def show(request):
    feature_ranks = FeatureRank.objects.all()
    features = groupby(feature_ranks, lambda fr: fr.feature)
    new_features = []
    for feature, it in features:
        feature.featureranks = list(it)
        new_features.append(feature)
    return render_to_response("bundesstats/show.html", RequestContext(request, {"features" : new_features }))
