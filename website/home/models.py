from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.user.username}"


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referrer = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
    contact_number = PhoneNumberField()
    paid = models.BooleanField(null=True, blank=True)
    order_id = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name}"

    @classmethod
    def filter_paid(cls):
        return cls.objects.filter(paid=True)


class Announcement(models.Model):
    title = models.CharField(max_length=80)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class EventCategory(models.Model):
    name = models.CharField(max_length=80)
    index = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Event Category'
        verbose_name_plural = 'Event Categories'
        ordering = ('index',)

    def __str__(self):
        return f"{self.name}"


def get_image_filename(instance, filename):
    title = instance.title
    slug = slugify(title)
    return "event_images/%s-%s" % (slug, filename)


class Event(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    date = models.DateField(blank=True, null=True)
    image_1 = models.ImageField(blank=True, null=True, upload_to=get_image_filename, verbose_name='First Image')
    image_2 = models.ImageField(blank=True, null=True, upload_to=get_image_filename, verbose_name='Second Image')
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)
    index = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ('index',)

    def __str__(self):
        return f"{self.title}, {self.category}"
