from django import forms
from django.utils import simplejson
from django.utils.safestring import mark_safe
import random

# modification of http://jannisleidel.com/2008/11/autocomplete-widget-for-django-tagging-form-fields/

class AutoCompleteInput(forms.TextInput):

    def __init__(self, *args, **kwargs):
        try:
            self.custom_queryset = kwargs.pop("custom_queryset")
        except KeyError:
            self.custom_queryset = []
        try:
            self.custom_displayfunc = kwargs.pop("custom_displayfunc")
        except KeyError:
            self.custom_displayfunc = unicode
        self.multiple = u""
        try:
            if kwargs.pop("autocomplete_multiple"):
                self.multiple = 'multiple: true,multipleSeparator: ",",'
        except KeyError:
            pass
        super(AutoCompleteInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if "id" in attrs:
            input_id = attrs["id"]
        else:
            input_id = "name_" + random.randint(1,10000)
        output = super(AutoCompleteInput, self).render(name, value, attrs)
        items = list(self.custom_queryset)
        item_list = simplejson.dumps([self.custom_displayfunc(item) for item in items],
                                    ensure_ascii=False)
        return output + mark_safe(u'''<script type="text/javascript">
            if(typeof autocompleteme == 'undefined'){var autocompleteme=[];}
            autocompleteme.push(["%s", %s,{width: 150, max: 10,%shighlight: false,scroll: true,scrollHeight: 300,matchContains: true,autoFill: true}]);
            </script>''' % (input_id, item_list, self.multiple))