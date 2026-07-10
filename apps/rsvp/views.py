import os
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import get_template
from django.conf import settings
from django.utils import timezone
from invitations.models import Invitation
from .models import Guest
from xhtml2pdf import pisa
from io import BytesIO

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
            return JsonResponse({'status': 'error', 'message': 'Token de invitado no válido.'}, status=400)
            
        if attending and number_of_companions > guest_obj.max_companions:
            return JsonResponse({
                'status': 'error', 
                'message': f'Solo puedes confirmar hasta {guest_obj.max_companions} acompañantes.'
            }, status=400)
            
        guest_obj.has_responded = True
        guest_obj.is_attending = attending
        guest_obj.confirmed_companions = number_of_companions if attending else 0
        guest_obj.dietary_restrictions = f"{dietary_restrictions}\n\nComentarios: {comments}"
        guest_obj.save()
        
    else:
        # It's a public RSVP
        if not invitation.allow_public_rsvp:
            return JsonResponse({'status': 'error', 'message': 'El RSVP público no está habilitado.'}, status=400)
            
        Guest.objects.create(
            invitation=invitation,
            name=guest_name,
            is_public_rsvp=True,
            has_responded=True,
            is_attending=attending,
            confirmed_companions=number_of_companions if attending else 0,
            dietary_restrictions=f"{dietary_restrictions}\n\nComentarios: {comments}"
        )
        
    return JsonResponse({'status': 'success', 'message': '¡Gracias por confirmar tu asistencia!'})


@staff_member_required
def generate_guest_pdf(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    invitation = guest.invitation
    
    # Message logic
    if invitation.default_pdf_message:
        message = invitation.default_pdf_message
    else:
        message = "Te invitamos cordialmente a celebrar este día tan especial con nosotros. Tu presencia es el mejor regalo."
        
    # Get the URL for the pass
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()
    link = f"{protocol}://{domain}/{invitation.slug}/?guest={guest.token}"
    
    if invitation.section_background_image:
        background_url = f"{protocol}://{domain}{settings.MEDIA_URL}{invitation.section_background_image.name}"
    else:
        background_url = f"{protocol}://{domain}{settings.STATIC_URL}img/fondo_floral.png"
    
    context = {
        'guest': guest,
        'invitation': invitation,
        'message': message,
        'link': link,
        'background_url': background_url,
        'MEDIA_URL': f"{protocol}://{domain}{settings.MEDIA_URL}" if settings.MEDIA_URL else "",
        'STATIC_URL': f"{protocol}://{domain}{settings.STATIC_URL}" if settings.STATIC_URL else ""
    }
    
    template_path = 'rsvp/guest_pdf.html'
    template = get_template(template_path)
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"Pase_{guest.name.replace(' ', '_')}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    
    return HttpResponse('Error generating PDF', status=400)
