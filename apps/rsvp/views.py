from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from invitations.models import Invitation
from .models import Guest

@require_POST
def submit_rsvp(request, slug):
    invitation = get_object_or_404(Invitation, slug=slug)
    
    # Check if there is a guest token
    token = request.POST.get('guest_token')
    
    effective_deadline = invitation.rsvp_deadline
    guest_obj = None
    if token:
        try:
            guest_obj = Guest.objects.get(token=token, invitation=invitation)
            if guest_obj.rsvp_deadline:
                effective_deadline = guest_obj.rsvp_deadline
        except Guest.DoesNotExist:
            pass
            
    if effective_deadline and timezone.now() > effective_deadline:
        return JsonResponse({'status': 'error', 'message': 'La fecha límite de confirmación ha expirado.'}, status=400)
    
    guest_name = request.POST.get('guest_name')
    attending = request.POST.get('attending') == 'true'
    
    try:
        number_of_companions = int(request.POST.get('number_of_companions', 0))
    except ValueError:
        number_of_companions = 0
        
    dietary_restrictions = request.POST.get('dietary_restrictions', '')
    comments = request.POST.get('comments', '')
    
    if token:
        # It's an invited guest
        if not guest_obj:
            return JsonResponse({'status': 'error', 'message': 'Invitado no válido.'}, status=400)
        guest = guest_obj
        
        # Validate companions max
        if number_of_companions > guest.max_companions:
            return JsonResponse({'status': 'error', 'message': f'Solo tienes permitido hasta {guest.max_companions} acompañantes.'}, status=400)
            
        guest.has_responded = True
        guest.is_attending = attending
        guest.confirmed_companions = number_of_companions if attending else 0
        guest.dietary_restrictions = f"{dietary_restrictions} | {comments}".strip(' |')
        guest.save()
        
    else:
        # It's a public RSVP
        if not guest_name:
            return JsonResponse({'status': 'error', 'message': 'El nombre es obligatorio'}, status=400)
            
        Guest.objects.create(
            invitation=invitation,
            name=guest_name,
            is_public_rsvp=True,
            has_responded=True,
            is_attending=attending,
            confirmed_companions=number_of_companions if attending else 0,
            dietary_restrictions=f"{dietary_restrictions} | {comments}".strip(' |')
        )
        
    return JsonResponse({'status': 'success', 'message': 'Confirmación guardada correctamente'})
