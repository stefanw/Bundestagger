# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter, force_escape
from django.utils.safestring import mark_safe
from django.conf import settings
import re

register = template.Library()

@register.filter
def hash(h, key):
    try:
        return h[key]
    except KeyError:
        return None

@register.filter
@stringfilter
def simple_formatting(value):
    value = force_escape(value)
    value = value.replace("\r\n", "\n")
    value = "<p>%s</p>" % value
    value = re.sub("(?sum) - (.*?)\n", "<li> - \\1</li>\n", value)
    value = re.sub("(?sum) ([a-z0-9]+\)) (.*?)\n", "<li> \\1 \\2</li>\n", value)
    value = re.sub("(?sum)((?:<li>.*?</li>\n)+)", "</p><ul>\\1</ul><p>", value)
    value = re.sub("(?sum)\n\n", "\n\n</p><p>", value)
    value = re.sub("(?sum)</ul><p>(\s+)</p><ul>", "</ul>\\1<ul>", value)
    value = re.sub("(?sum)</p><p>(\s+)</p><p>", "\\1</p><p>", value)
    value = re.sub("(?sum)([^(?:</li>|</ul>|\n)])\n([^(?:</p>|<li>|\n</p>|<ul>)])", "\\1<br/>\n\\2", value)
    return mark_safe(value)

    
if __name__ == "__main__":
    text="""Die Sitzung ist eröffnet.
Ich begrüße Sie alle herzlich. bis 22c auf:

 - ERstens
 - Zweitens

 a) Beratung des Antrags der B
 b) Erste Beratung des von der
 c) Erste Beratung des vom

Hier handelt es sich um Überweisungen. Ungültig sind wie immer – –"""
    print simple_formatting(text)