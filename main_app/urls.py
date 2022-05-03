from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('events/create/', views.EventCreate.as_view(), name='events_create'),
    path('events/', views.events_index, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<str:event_id>/create', views.ticketmaster_create, name='ticketmaster_create'),
    path('events/<int:event_id>/create_comment', views.create_comment, name="create_comment"),
    path('events/<int:event_id>/delete/<int:comment_id>', views.delete_comment, name="delete_comment"),
    path('events/search/', views.search, name="search"),
    path('user/', views.user_detail, name='user_detail'),
    path('user/add_photo/<int:user_id>', views.add_photo, name='add_photo'),
    path('events/<int:event_id>/<int:user_id>', views.going_event, name='going_event'),
    path('user/create', views.create_user, name='create_user'),
    path('user/add_bio/<int:user_id>', views.add_bio, name='add_bio'),
    path('user/<int:user_id>/not_going/<int:event_id>', views.not_going, name='not_going'),
    path('events/<int:event_id>/update/<int:comment_id>', views.update_comment, name='update_comment'),
]