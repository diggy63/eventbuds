from ast import Delete
from email.mime import image
from operator import indexOf
from queue import Empty
from tabnanny import check
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from dotenv import load_dotenv
from psycopg2 import Date
import urllib
from .models import Event, Comment, TicketMasterEvent
import requests, os
from .models import Event, Comment, User_Avatar, User_Event, User
import uuid
import boto3

S3_BASE_URL = 'https://s3.us-west-1.amazonaws.com/'
BUCKET = 'catcollectorbucketdk'

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
            return redirect('create_user')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@login_required
def events_index(request):
    events = Event.objects.all()
    return render(request, 'events/index.html', {'events': events})

@login_required
def event_detail(request, event_id , user_id):
    show_going = True
    event = Event.objects.get(id=event_id)
    user = User_Avatar.objects.get(user_id = user_id)
    try:
        user_event = User_Event.objects.get(user = user, event_id = event_id)
        show_going = False
    except:
        show_going = True
    return render(request, 'events/detail.html', {'event':event , 'show_going': show_going} )


@login_required    
def create_event(request):
    return render(request, 'events/create.html')
  
@login_required    
def new_event(request, user_id):
    photo_file = request.FILES.get('photo', None)
    print(request.FILES)
    event = Event.objects.create(
        event_name=request.POST.get('event_name'),
        event_type=request.POST.get('event_type'),
        location=request.POST.get('location'),
        artist=request.POST.get('artist'),
        description=request.POST.get('description'),
        date=request.POST.get('date'),
        user_id=user_id
        )
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            event.image = url
            print(event.image)
            print("photo was sucessful")
        except:
            print('An error occurred uploading to S3.')
    event.save()
    return redirect('/events/')

@login_required
def create_comment(request, event_id, user_id):
    event = Event.objects.get(id=event_id)
    comment = Comment.objects.create(user=request.user, event=event, content=request.POST.get('content', ''))
    return redirect(f'/events/{event_id}/{user_id}')

@login_required
def delete_comment(request, event_id, comment_id, user_id):
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return redirect(f'/events/{event_id}/{user_id}')

@login_required
def update_comment(request, event_id, comment_id, user_id):
    comment = Comment.objects.get(id=comment_id)
    return render(request, 'comment/update.html', {'comment': comment, 'event_id': event_id, 'user_id':user_id}) 

@login_required
def update_content(request, event_id, comment_id, user_id):
    comment = Comment.objects.get(id=comment_id)
    content = request.POST.get('content')
    comment.content = content
    comment.save()
    
    return redirect(f'/events/{event_id}/{user_id}')
    
@login_required
def search(request):
    load_dotenv()
    query = request.GET.get('q')
    key = os.getenv('ACCESS_TOKEN')
    r = requests.get(f'https://app.ticketmaster.com/discovery/v2/events.json?keyword={query}&apikey={key}')
    r_json = r.json()
    embed = r_json.get('_embedded', {})
    events = embed.get('events', [])
    for idx, event in enumerate(events): # transforms the json so that venues is accessible with . notation
        embed = event.get('_embedded', {})
        venues = embed.get('venues', [])
        events[idx]['venues'] = venues
    return render(request, 'events/search.html', {'events': events})

@login_required
def user_detail(request, user_id):
    viewUser = User_Avatar.objects.get(user_id=user_id)
    return render(request, 'user/detail.html', {'ownerUser': viewUser})

@login_required
def add_photo(request, user_id):
  # photo-file will be the "name" attribute on the <input type="file">
  photo_file = request.FILES.get('photo-file', None)
  user_bio = request.POST.get('bio', None)
  User_Avatar.objects.create(user_id=user_id, bio= user_bio)
  user = User_Avatar.objects.get(user_id= user_id)
  if photo_file:
    s3 = boto3.client('s3')
    # need a unique "key" for S3 / needs image file extension too
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    # just in case something goes wrong
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      #build the full url string
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      # we can assign to cat_id or cat (if you have a cat object)
      user.url = url
      user.save()
      print("photo was sucessful")
    except:
      print('An error occurred uploading to S3.')
  return redirect(f'/user/{user_id}')

@login_required
def going_event(request, event_id, user_id):
    user = User_Avatar.objects.get(user_id=user_id)
    event = Event.objects.get(id=event_id)
    try:
        event_user = User_Event.objects.get(user=user, event=event)
    except:
        user_event = User_Event.objects.create(user=user, event=event)
        user_event.save()
    return redirect(f'/user/{user_id}')

@login_required
def ticketmaster_create(request, event_id, user_id):
    load_dotenv()
    key = os.getenv('ACCESS_TOKEN')
    r = requests.get(f'https://app.ticketmaster.com/discovery/v2/events.json?id={event_id}&apikey={key}')
    r_json = r.json()
    embed = r_json.get('_embedded', {})
    events = embed.get('events', [])
    the_event = events[0]
    second_embed = the_event.get('_embedded', {})
    if second_embed:
        event_name = the_event['name']
        event_type = the_event.get('classifications', [])
        if event_type:
            event_type = event_type[0]['segment']['name']
        else:
            event_type = 'None'
        location = the_event['_embedded']['venues'][0].get('name', 'None')
        artist = the_event['_embedded'].get('attractions', [])
        if artist:
            artist = artist[0]['name']
        else:
            artist = 'None'
        date = the_event['dates']['start']['localDate']
        event_image = the_event.get('images', [])
        if event_image:
            event_image = event_image[0]['url']
        else:
            event_image = 'None'
        
        event = TicketMasterEvent.objects.get_or_create(url_ticketmaster = event_id, defaults={
                    'event_name':event_name,
                    'event_type':event_type,
                    'location': location,
                    'artist':artist,
                    'image':event_image,
                    'description':'None',
                    'date':date})
        return redirect(f'/events/{TicketMasterEvent.objects.get(url_ticketmaster=event_id).id}/{user_id}')
    else:
        return redirect(f'/events/search')  

@login_required
def create_user(request):
    return render(request, 'user/create.html')

@login_required
def add_bio(request, user_id):
    user = User_Avatar.objects.get(user_id=user_id)
    user.bio = request.GET.get('bio')
    user.save()
    return redirect('/user')

@login_required
def not_going(request, user_id, event_id):
    user = User_Avatar.objects.get(user_id=user_id)
    event = Event.objects.get(id=event_id)
    delete_connect = User_Event.objects.get(user=user, event=event)
    delete_connect.delete()
    return redirect(f'/user/{user_id}')

@login_required
def update_event(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(request, 'events/update.html', {'event': event})  

@login_required
def update_details(request, event_id, user_id):
    photo_file = request.FILES.get('photo', None)
    event = Event.objects.get(id=event_id)
    event.event_name = request.POST.get('event_name')
    event.event_type = request.POST.get('event_type')
    event.location = request.POST.get('location')
    event.artist = request.POST.get('artist')
    event.description = request.POST.get('description')
    # if there is no date given their will be an error
    # so we must check because date feilds cant be null
    if request.POST.get('date') == "":
        print('nodate')
    else:
        event.date = request.POST.get('date')
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            event.image = url
            print("photo was sucessful")
        except:
            print('An error occurred uploading to S3.')
    event.save()
    return redirect(f'/events/{event_id}/{user_id}')

class EventDelete(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = '/events/'

@login_required
def get_update(request, user_id):
    viewUser = User_Avatar.objects.get(id=user_id)
    return render(request, 'user/update.html', {'ownerUser': viewUser})

@login_required
def update_profile(request, user_id):
    userView = User_Avatar.objects.get(id=user_id)
    photo_file = request.FILES.get('photo-file', None)
    user_bio = request.POST.get('bio', None)
    user_name = request.POST.get('username', None)
    try:
        check_name = User.objects.get(username=user_name)
        if check_name.id != user_id:
            error_name = "Username already taken."
            return render(request, 'user/update.html', {'ownerUser': userView, 'error_name':error_name})
    except:
        print("New username added!")
    userView.bio = user_bio
    userView.user.username = user_name
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            #build the full url string
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            userView.url = url
            print("Photo upload sucessful.")
        except:
            print('An error occurred uploading to S3.')
    userView.user.save()           
    userView.save()
    return redirect(f'/user/{userView.user.id}')

@login_required
def add_comment(request, user_id):
    userProfile = User_Avatar.objects.get(user_id=user_id)
    comment = Comment.objects.create(user=request.user, profile=userProfile, content=request.POST.get('content', ''))
    comment.save()
    return redirect(f'/user/{user_id}')

@login_required
def delete_profile_comment(request, user_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return redirect(f'/user/{user_id}')
