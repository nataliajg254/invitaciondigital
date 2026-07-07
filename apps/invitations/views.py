from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Invitation
from rsvp.models import Guest

def invitation_detail(request, slug):
    invitation = get_object_or_404(Invitation, slug=slug)
    
    template_name = f"{invitation.template_choice}/index.html"
    
    guest_token = request.GET.get('guest')
    current_guest = None
    if guest_token:
        try:
            current_guest = Guest.objects.get(token=guest_token, invitation=invitation)
        except (Guest.DoesNotExist, ValueError):
            pass
            
    effective_deadline = invitation.rsvp_deadline
    if current_guest and current_guest.rsvp_deadline:
        effective_deadline = current_guest.rsvp_deadline
        
    rsvp_expired = False
    if effective_deadline and timezone.now() > effective_deadline:
        rsvp_expired = True

    sections = [
        ('countdown', invitation.order_countdown),
        ('ceremony', invitation.order_ceremony),
        ('location', invitation.order_location),
        ('program', invitation.order_program),
        ('parents', invitation.order_parents),
        ('sponsors', invitation.order_sponsors),
        ('gallery', invitation.order_gallery),
        ('gift_table', invitation.order_gift_table),
        ('dress_code', invitation.order_dress_code),
        ('rsvp', invitation.order_rsvp),
    ]
    sections.sort(key=lambda x: x[1])
    ordered_sections = [s[0] for s in sections]

    context = {
        'invitation': invitation,
        'current_guest': current_guest,
        'rsvp_expired': rsvp_expired,
        'effective_deadline': effective_deadline,
        'ordered_sections': ordered_sections,
    }
    return render(request, template_name, context)
