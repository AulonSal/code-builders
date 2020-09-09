from django.db import models
from django.contrib.auth.models import User


class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=16)


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referrer = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
    contact_number = models.CharField(max_length=14)
