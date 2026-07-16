from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from invitations.models import Invitation

@login_required
def portal_dashboard(request):
    if request.user.is_staff:
        # El staff ve todas las invitaciones
        invitations = Invitation.objects.all().order_by('-event_date')
    else:
        # El cliente ve solo las invitaciones que administra o atiende en recepción
        invitations = (
            Invitation.objects.filter(administrators=request.user)
            | Invitation.objects.filter(hostesses=request.user)
        ).distinct().order_by('-event_date')
        
    return render(request, 'portal/dashboard.html', {'invitations': invitations})
