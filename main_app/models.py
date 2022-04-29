from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Event(models.Model):
    event_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    image = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    date = models.DateField()
    url_ticketmaster = models.CharField(max_length=100)
    user = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.event_name

    def get_absolute_url(self):
        return reverse('home')

class Comment(models.Model):
    content = models.TextField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.content