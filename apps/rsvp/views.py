import json
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import get_template
from django.conf import settings
from django.utils import timezone
from invitations.models import Invitation
from .models import Guest
from xhtml2pdf import pisa
from io import BytesIO
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from django.db import transaction

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
        return JsonResponse({
            'status': 'error',
            'message': 'Necesitas un enlace personalizado para confirmar asistencia.'
        }, status=400)
        
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


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

def check_invitation_access(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, slug, *args, **kwargs):
        invitation = get_object_or_404(Invitation, slug=slug)
        has_access = invitation.administrators.filter(pk=request.user.pk).exists()
        if not request.user.is_staff and not has_access:
            raise PermissionDenied("No tienes permiso para administrar esta invitación.")
        return view_func(request, slug, *args, **kwargs)
    return _wrapped_view

# --- GUEST DASHBOARD ENDPOINTS ---

def is_mobile_request(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if not user_agent:
        return False

    tablet_indicators = ('ipad', 'tablet')
    if any(indicator in user_agent for indicator in tablet_indicators):
        return False

    if 'android' in user_agent and 'mobile' not in user_agent:
        return False

    mobile_indicators = (
        'iphone',
        'ipod',
        'android',
        'windows phone',
        'blackberry',
        'opera mini',
        'iemobile',
    )
    return any(indicator in user_agent for indicator in mobile_indicators)


@check_invitation_access
@ensure_csrf_cookie
def guest_dashboard(request, slug):
    invitation = get_object_or_404(Invitation, slug=slug)
    template_name = 'rsvp_mobile_guest_dashboard.html' if is_mobile_request(request) else 'rsvp_guest_dashboard.html'
    return render(request, template_name, {'invitation': invitation})


@check_invitation_access
@require_http_methods(["GET", "POST"])
def api_guests_list_create(request, slug):
    invitation = get_object_or_404(Invitation, slug=slug)
    
    if request.method == "GET":
        guests = Guest.objects.filter(invitation=invitation).order_by('-created_at')
        data = [{
            'id': g.id,
            'name': g.name,
            'phone_number': g.phone_number,
            'max_companions': g.max_companions,
            'has_responded': g.has_responded,
            'is_attending': g.is_attending,
            'confirmed_companions': g.confirmed_companions,
            'token': g.token,
            'sheet_name': g.sheet_name
        } for g in guests]
        return JsonResponse(data, safe=False)
        
    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            guest = Guest.objects.create(
                invitation=invitation,
                name=body.get('name'),
                phone_number=body.get('phone_number', ''),
                max_companions=int(body.get('max_companions', 1))
            )
            return JsonResponse({'status': 'success', 'id': guest.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@check_invitation_access
@require_http_methods(["PUT", "DELETE"])
def api_guest_detail(request, slug, guest_id):
    invitation = get_object_or_404(Invitation, slug=slug)
    guest = get_object_or_404(Guest, id=guest_id, invitation=invitation)
    
    if request.method == "PUT":
        try:
            body = json.loads(request.body)
            guest.name = body.get('name', guest.name)
            guest.phone_number = body.get('phone_number', guest.phone_number)
            guest.max_companions = int(body.get('max_companions', guest.max_companions))
            guest.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    elif request.method == "DELETE":
        guest.delete()
        return JsonResponse({'status': 'success'}, status=204)


@check_invitation_access
@require_http_methods(["GET"])
def api_download_excel_template(request, slug):
    invitation = get_object_or_404(Invitation, slug=slug)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invitados"
    
    # Headers
    headers = ["Nombre del Invitado o Familia", "Teléfono (WhatsApp)", "Número de Pases (Lugares)"]
    ws.append(headers)
    
    # Styling headers
    header_fill = PatternFill(start_color="4f46e5", end_color="4f46e5", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        
    # Adjust column widths
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 25
    
    # Add an example row
    ws.append(["Familia Ejemplo", "5215512345678", 4])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Plantilla_Invitados.xlsx"'
    wb.save(response)
    
    return response


@check_invitation_access
@require_http_methods(["POST"])
def api_upload_excel_guests(request, slug):
    invitation = get_object_or_404(Invitation, slug=slug)
    
    if 'file' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'No se encontró archivo'}, status=400)
        
    excel_file = request.FILES['file']
    
    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb.active
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Archivo Excel inválido o corrupto.'}, status=400)
        
    # Validation and Atomic Transaction
    created_count = 0
    updated_count = 0
    
    try:
        with transaction.atomic():
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not row or not row[0]:
                        continue  # Skip empty rows or rows without name
                        
                    name = str(row[0]).strip()
                    
                    # Parse phone carefully to remove decimal points if stored as numeric float in Excel
                    phone = ""
                    if row[1] is not None:
                        val = row[1]
                        if isinstance(val, float):
                            phone = str(int(val)) if val.is_integer() else str(val)
                        elif isinstance(val, int):
                            phone = str(val)
                        else:
                            phone = str(val).strip()
                            if phone.endswith('.0'):
                                phone = phone[:-2]
                    
                    # Try to parse passes
                    try:
                        passes = int(row[2])
                    except (ValueError, TypeError):
                        passes = 1  # Default to 1 pass if invalid
                        
                    if not name:
                        continue
                        
                    # Search for duplicate: by phone first, then by name
                    guest = None
                    if phone:
                        guest = Guest.objects.filter(invitation=invitation, phone_number=phone).first()
                    if not guest:
                        guest = Guest.objects.filter(invitation=invitation, name=name).first()
                        
                    if guest:
                        # Update existing guest
                        guest.name = name
                        if phone:
                            guest.phone_number = phone
                        guest.max_companions = passes
                        guest.sheet_name = sheet_name
                        guest.created_by = request.user
                        guest.save()
                        updated_count += 1
                    else:
                        # Create new guest
                        Guest.objects.create(
                            invitation=invitation,
                            name=name,
                            phone_number=phone,
                            max_companions=passes,
                            sheet_name=sheet_name,
                            created_by=request.user
                        )
                        created_count += 1
                    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error procesando el archivo: {str(e)}'}, status=400)
        
    return JsonResponse({
        'status': 'success', 
        'message': f'Importación completada: {created_count} creados, {updated_count} actualizados.'
    })
