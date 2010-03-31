from django import forms
# from django.utils.translation import ugettext_lazy as _
#from annotate.widgets import ColorWidget
import re

class EditSpeechPartForm(forms.Form):
    text = forms.CharField(required=True)
