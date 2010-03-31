# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter, escape
from django.utils.safestring import mark_safe
from django.conf import settings
import re

register = template.Library()

@register.tag(name='get_googlecharts_url')
def do_get_googlecharts_url(parser, token):
    """
    """
    try:
        contents = token.split_contents()
        instance_name = contents[1]
    except (ValueError, IndexError):
        raise template.TemplateSyntaxError, "%r tag requires two or three arguments" % token.contents.split()[0]
    return GoogleChartsNode(instance_name)

class GoogleChartsNode(template.Node):
    def __init__(self, feature):
        self.feature = template.Variable(feature)

    def render(self, context):
        feature = self.feature.resolve(context)
        url = "http://chart.apis.google.com/chart?"
        params = []
        params.append(feature.url_parameters)
        params.append("chf=bg,s,65432100")
        if feature.display_rest:
            addup = sum(map(lambda x: x.value, feature.featureranks))
        else:
            addup = sum(map(lambda x: x.value, [featurerank for featurerank in feature.featureranks if (featurerank.politician is not None or featurerank.party is not None)]))
        datapoints = []
        labels = []
        colors = []
        featureranks = sorted(feature.featureranks, key=lambda x: x.value, reverse=True)
        for featurerank in featureranks:
            if not feature.display_rest and (featurerank.politician is None and featurerank.party is None):
                continue
            datapoints.append(unicode(round(float(featurerank.value)/addup * 100, 1)))
            labels.append("%s [%d]" % (unicode(featurerank), featurerank.value))
        params.append("chd=t:"+",".join(datapoints))
        params.append("chl="+"|".join(labels))
        url += "&".join(params)
        return url