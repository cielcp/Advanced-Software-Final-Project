from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime, time
from django.utils import timezone
from datetime import datetime, timedelta, tzinfo

def one_hour_hence():
    return timezone.now() + timedelta(hours=1)

class Event(models.Model):
    event_id = models.CharField(max_length=150, default="UNKNOWN")
    host_user = models.CharField(max_length=150, default="UNKNOWN")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    start_datetime = models.DateTimeField(default=timezone.now)
    #start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(default=one_hour_hence)


    def __str__(self):
        return self.name

    def get_rsvps(self):
        return list(Rsvp.objects.all().filter(event_id=self.pk))

def get_default_event():
    # Your logic to determine the default event here
    if Event.objects.first():
        return Event.objects.first()
    else:
        default_event = Event(name='very first event', description='description', address='Univeristy of Virginia', latitude=38.033554, longitude=-78.507980, start=None, end=None)
        return default_event

class Rsvp(models.Model):
    event_id = models.CharField(default="UNKNOWN", max_length=150)
    username = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    note = models.TextField(blank = True)
    datetime = models.DateTimeField("date submitted")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    has_chosen_role = models.BooleanField(default=False)

    def set_role(self, role):
        if role == 'admin':
            self.user.is_staff = True
        else:
            self.user.is_staff = False
        self.has_chosen_role = True
        self.user.save()
        self.save()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created or not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
