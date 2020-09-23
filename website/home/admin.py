from django.contrib import admin

from .models import TeamMember, Participant, Announcement, EventCategory, Event, User


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('created_on',)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'paid', 'contact_number', 'referrer', 'order_id')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(TeamMember)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Announcement)
admin.site.register(EventCategory)
admin.site.register(Event, EventAdmin)
