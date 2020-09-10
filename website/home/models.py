from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=16)


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referrer = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
    contact_number = PhoneNumberField()


class Announcement(models.Model):
    title = models.CharField(max_length=80)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now=True)


class EventCategory(models.Model):
    type = models.CharField(max_length=80)


class Event(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    date = models.DateField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)
