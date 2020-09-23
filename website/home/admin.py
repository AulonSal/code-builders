from django.contrib import admin

from .models import TeamMember, Participant, Announcement, EventCategory, Event


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('created_on',)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'paid', 'contact_number', 'referrer', 'order_id')


admin.site.register(TeamMember)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Announcement)
admin.site.register(EventCategory)
admin.site.register(Event, EventAdmin)
