from django.urls import path
from . import views
from rsvp.views import guest_dashboard, api_guests_list_create, api_guest_detail

app_name = 'invitations'

urlpatterns = [
    # Guest Dashboard UI
    path('<slug:slug>/dashboard/', guest_dashboard, name='dashboard'),
    
    # Guest Dashboard API Endpoints
    path('api/<slug:slug>/guests/', api_guests_list_create, name='api_guests_list_create'),
    path('api/<slug:slug>/guests/<int:guest_id>/', api_guest_detail, name='api_guest_detail'),

    # Invitation detail MUST be last so it doesn't catch "dashboard" or "api" as slugs
    path('<slug:slug>/', views.invitation_detail, name='detail'),
]
