from django.template import Library, Node, TemplateSyntaxError
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from bundestagger.bundestagging.forms import TagsForm

register = Library()
        
class TagsFormNode(Node):
    def __init__(self, context_var):
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = TagsForm(auto_id=False)
        return ''
        
def do_tagsform(parser, token):
    bits = token.contents.split()
    if len(bits)!=3 and bits[1]!="as":
        raise TemplateSyntaxError("Need as [context variable]")
    return TagsFormNode(bits[2])
    
def get_contenttype_kwargs(content_object):
    """
    Gets the basic kwargs necessary for almost all of the following tags.
    """
    kwargs = {
        'content_type' : ContentType.objects.get_for_model(content_object).id,
        'object_id' : getattr(content_object, 'pk', getattr(content_object, 'id')),
    }
    return kwargs

def get_add_tags_url(content_object, parent=None):
    kwargs = get_contenttype_kwargs(content_object)
    return reverse('tagging_add-tags', kwargs=kwargs)


register.tag('tagsform', do_tagsform)
register.simple_tag(get_add_tags_url)