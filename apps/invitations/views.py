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
        {'type': 'countdown', 'order': invitation.order_countdown},
        {'type': 'ceremony', 'order': invitation.order_ceremony},
        {'type': 'location', 'order': invitation.order_location},
        {'type': 'program', 'order': invitation.order_program},
        {'type': 'parents', 'order': invitation.order_parents},
        {'type': 'sponsors', 'order': invitation.order_sponsors},
        {'type': 'gallery', 'order': invitation.order_gallery},
        {'type': 'gift_table', 'order': invitation.order_gift_table},
        {'type': 'dress_code', 'order': invitation.order_dress_code},
        {'type': 'rsvp', 'order': invitation.order_rsvp},
        {'type': 'closing_message', 'order': invitation.order_closing_message},
    ]
    
    for sep in invitation.separator_images.all():
        if sep.image:
            sections.append({'type': 'separator', 'order': sep.order, 'image_url': sep.image.url})
            
    sections.sort(key=lambda x: x['order'])
    ordered_sections = sections

    context = {
        'invitation': invitation,
        'current_guest': current_guest,
        'rsvp_expired': rsvp_expired,
        'effective_deadline': effective_deadline,
        'ordered_sections': ordered_sections,
    }
    return render(request, template_name, context)
