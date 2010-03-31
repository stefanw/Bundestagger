from django.contrib import admin
from models import *

class SpeechPartAdmin(admin.ModelAdmin):
    list_display = ('ordernr', 'speech',)
    ordering = ("ordernr",)
    exclude = ("speech",)
    
class PoliticianAdmin(admin.ModelAdmin):
    list_display = ('name', 'party',)
    search_fields = ["first_name", "last_name"]

class EventAdmin(admin.ModelAdmin):
    exclude = ("context",)
    
class MemberOfParliamentAdmin(admin.ModelAdmin):
    search_fields = ["politician__first_name", "politician__last_name"]

class TopSpeakerAdmin(admin.ModelAdmin):
    exclude = ("top",)

admin.site.register(Party)
admin.site.register(Event, EventAdmin)
admin.site.register(SpeechPart, SpeechPartAdmin)
admin.site.register(Speech)
admin.site.register(ParliamentSession)
admin.site.register(Parliament)
admin.site.register(MemberOfParliament, MemberOfParliamentAdmin)
admin.site.register(Politician, PoliticianAdmin)
admin.site.register(SessionTop)
admin.site.register(TopSpeaker, TopSpeakerAdmin)
admin.site.register(Attachment)
admin.site.register(Poll)
admin.site.register(PollVote)