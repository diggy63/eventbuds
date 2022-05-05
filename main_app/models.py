from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Event(models.Model):
    event_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    image = models.TextField(max_length=250)
    description = models.TextField(max_length=200)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.event_name}'

    def get_absolute_url(self):
        return reverse('home')

class User_Avatar(models.Model):
    url = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=200)

    def __str__(self):
        return f"Avatar for user_id: {self.user_id}."

class Comment(models.Model):
    content = models.TextField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    profile = models.ForeignKey(User_Avatar, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.content

class User_Event(models.Model):
    user = models.ForeignKey(User_Avatar, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} {self.event}'

class TicketMasterEvent(Event):
        url_ticketmaster = models.CharField(max_length=100, unique=True)
