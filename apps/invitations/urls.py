from django.urls import path
from . import views

app_name = 'invitations'

urlpatterns = [
    path('<slug:slug>/', views.invitation_detail, name='detail'),
]
