from operator import indexOf
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from dotenv import load_dotenv
from .models import Event, Comment
import requests, os

# Create your views here.
def home(request):
    return render(request, 'index.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in via code
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

def events_index(request):
    events = Event.objects.all()
    return render(request, 'events/index.html', {'events': events})

def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(request, 'events/detail.html', {'event': event})
class EventCreate(CreateView):
    model = Event
    fields = '__all__'

def create_comment(request, event_id):
    event = Event.objects.get(id=event_id)
    comment = Comment.objects.create(user=request.user, event=event, content=request.POST.get('content', ''))
    return redirect('event_detail', event_id=event_id)

def delete_comment(request, event_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return redirect('event_detail', event_id=event_id)

def search(request):
    load_dotenv()
    query = request.GET.get('q')
    key = os.getenv('ACCESS_TOKEN')
    r = requests.get(f'https://app.ticketmaster.com/discovery/v2/events.json?keyword={query}&apikey={key}')
    r_json = r.json()
    embed = r_json.get('_embedded', {})
    events = embed.get('events', [])
    for idx, event in enumerate(events):
        embed = event.get('_embedded')
        venues = embed.get('venues')
        events[idx]['venues'] = venues
    print(events)
    return render(request, 'events/search.html', {'events': events})
    