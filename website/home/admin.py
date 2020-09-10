from django.contrib import admin

from .models import TeamMember, Participant, Announcement, EventCategory, Event


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('created_on',)


admin.site.register(TeamMember)
admin.site.register(Participant)
admin.site.register(Announcement)
admin.site.register(EventCategory)
admin.site.register(Event, EventAdmin)
