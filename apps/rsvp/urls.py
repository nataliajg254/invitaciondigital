from django.urls import path
from . import views

app_name = 'rsvp'

urlpatterns = [
    path('<slug:slug>/submit/', views.submit_rsvp, name='submit'),
]
