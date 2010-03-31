# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from models import ParliamentSession

class LatestSessionsFeed(Feed):
    title = "Letzte Bundestagsitzungen auf BundesTagger"
    link = "/"
    description = "Letzte Sitzungen des Bundestages auf BundesTagger.de"
    description_template = "bundestag/session_description.html"

    def items(self):
        return ParliamentSession.objects.order_by('-date')[:10]
        
class LatestSessionsFeedAtom(LatestSessionsFeed):
    feed_type = Atom1Feed
    subtitle = LatestSessionsFeed.description