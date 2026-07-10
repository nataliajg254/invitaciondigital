from django.urls import path
from . import views

app_name = 'rsvp'

urlpatterns = [
    path('<slug:slug>/submit/', views.submit_rsvp, name='submit'),
    path('pdf/<int:guest_id>/', views.generate_guest_pdf, name='generate_guest_pdf'),
]
