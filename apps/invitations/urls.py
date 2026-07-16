from django.urls import path
from . import views
from rsvp.views import (
    guest_dashboard,
    hostess_dashboard,
    api_guests_list_create,
    api_guest_detail,
    api_guest_whatsapp_sent,
    api_whatsapp_messages,
    api_guest_whatsapp_message_preview,
    api_download_excel_template,
    api_upload_excel_guests,
    api_hostesses_list_create,
    api_hostess_detail,
    api_hostess_guests,
    api_hostess_check_in,
)

app_name = 'invitations'

urlpatterns = [
    # Guest Dashboard UI
    path('<slug:slug>/dashboard/', guest_dashboard, name='dashboard'),
    path('<slug:slug>/hostess/', hostess_dashboard, name='hostess_dashboard'),
    
    # Guest Dashboard API Endpoints
    path('api/<slug:slug>/guests/', api_guests_list_create, name='api_guests_list_create'),
    path('api/<slug:slug>/hostesses/', api_hostesses_list_create, name='api_hostesses_list_create'),
    path('api/<slug:slug>/hostesses/<int:user_id>/', api_hostess_detail, name='api_hostess_detail'),
    path('api/<slug:slug>/hostess/guests/', api_hostess_guests, name='api_hostess_guests'),
    path('api/<slug:slug>/hostess/check-in/', api_hostess_check_in, name='api_hostess_check_in'),
    path('api/<slug:slug>/whatsapp-messages/', api_whatsapp_messages, name='api_whatsapp_messages'),
    path('api/<slug:slug>/guests/excel-template/', api_download_excel_template, name='api_download_excel_template'),
    path('api/<slug:slug>/guests/excel-upload/', api_upload_excel_guests, name='api_upload_excel_guests'),
    path('api/<slug:slug>/guests/<int:guest_id>/whatsapp-message-preview/', api_guest_whatsapp_message_preview, name='api_guest_whatsapp_message_preview'),
    path('api/<slug:slug>/guests/<int:guest_id>/whatsapp-sent/', api_guest_whatsapp_sent, name='api_guest_whatsapp_sent'),
    path('api/<slug:slug>/guests/<int:guest_id>/', api_guest_detail, name='api_guest_detail'),

    # Invitation detail MUST be last so it doesn't catch "dashboard" or "api" as slugs
    path('<slug:slug>/', views.invitation_detail, name='detail'),
]
