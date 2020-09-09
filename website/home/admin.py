from django.contrib import admin

from .models import TeamMember, Participant

# Register your models here.
admin.site.register(TeamMember)
admin.site.register(Participant)
