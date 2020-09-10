from django.contrib import admin

from .models import TeamMember, Participant, Announcement, EventCategory, Event

admin.site.register(TeamMember)
admin.site.register(Participant)
admin.site.register(Announcement)
admin.site.register(EventCategory)
admin.site.register(Event)
