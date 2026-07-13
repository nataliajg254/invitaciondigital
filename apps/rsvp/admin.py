import urllib.parse
import re
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from .models import Guest


def normalize_whatsapp_phone(phone_number):
    digits = re.sub(r'\D', '', phone_number or '')
    if len(digits) == 13 and digits.startswith('521'):
        return f"52{digits[3:]}"
    return digits

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'max_companions', 'is_attending', 'has_responded', 'whatsapp_link', 'pdf_link')
    list_filter = ('has_responded', 'is_attending', 'is_public_rsvp', 'invitation')
    search_fields = ('name', 'phone_number')
    readonly_fields = ('token', 'has_responded', 'is_attending', 'confirmed_companions', 'dietary_restrictions', 'created_at', 'is_public_rsvp')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:guest_id>/whatsapp/',
                self.admin_site.admin_view(self.whatsapp_redirect),
                name='rsvp_guest_whatsapp',
            ),
        ]
        return custom_urls + urls
    
    def whatsapp_link(self, obj):
        if not obj.phone_number:
            return "-"

        url = reverse('admin:rsvp_guest_whatsapp', args=[obj.pk])
        return format_html('<a href="{}" target="_blank" style="background-color:#25D366; color:white; padding:5px 10px; border-radius:4px; font-weight:bold; text-decoration:none;">Enviar WhatsApp</a>', url)
    
    whatsapp_link.short_description = "WhatsApp"

    def whatsapp_redirect(self, request, guest_id):
        guest = get_object_or_404(Guest, pk=guest_id)
        phone_number = normalize_whatsapp_phone(guest.phone_number)

        if not phone_number:
            messages.error(request, "Este invitado no tiene un teléfono válido para WhatsApp.")
            return redirect(reverse('admin:rsvp_guest_change', args=[guest.pk]))

        invitation_path = reverse('invitations:detail', args=[guest.invitation.slug])
        invitation_url = request.build_absolute_uri(f'{invitation_path}?guest={guest.token}')
        message = (
            f"¡Hola {guest.name}! Te invito cordialmente a mi evento. 🥳\n\n"
            "En el siguiente enlace puedes ver todos los detalles y confirmar tu asistencia:\n"
            f"{invitation_url}\n\n"
            "¡Te espero con mucha emoción!"
        )
        encoded_message = urllib.parse.quote(message)
        return redirect(f'https://wa.me/{phone_number}?text={encoded_message}')

    def pdf_link(self, obj):
        url = reverse('rsvp:generate_guest_pdf', args=[obj.id])
        return format_html('<a href="{}" class="button" target="_blank">Descargar PDF</a>', url)
    pdf_link.short_description = 'Pase PDF'
    
    def get_fieldsets(self, request, obj=None):
        return (
            ('Información Principal', {
                'fields': ('invitation', 'name', 'phone_number', 'max_companions')
            }),
            ('Opciones Avanzadas', {
                'fields': ('rsvp_deadline', 'is_public_rsvp', 'token'),
                'classes': ('collapse',)
            }),
            ('Estado de Confirmación', {
                'fields': ('has_responded', 'is_attending', 'confirmed_companions', 'dietary_restrictions'),
                'classes': ('collapse',)
            }),
        )
