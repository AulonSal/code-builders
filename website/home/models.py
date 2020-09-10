from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.user.first_name}"


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referrer = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
    contact_number = PhoneNumberField()

    def __str__(self):
        return f"{self.user.first_name}"


class Announcement(models.Model):
    title = models.CharField(max_length=80)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class EventCategory(models.Model):
    type = models.CharField(max_length=80)

    class Meta:
        verbose_name = 'Event Category'
        verbose_name_plural = 'Event Categories'

    def __str__(self):
        return f"{self.type}"


class Event(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    date = models.DateField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title}, {self.category}"
