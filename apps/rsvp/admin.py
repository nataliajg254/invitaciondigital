import urllib.parse
import re
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from .models import Guest, GuestCheckIn, GuestVisit
from .whatsapp_messages import get_whatsapp_message_template, render_whatsapp_message


def normalize_whatsapp_phone(phone_number):
    digits = re.sub(r'\D', '', phone_number or '')
    if len(digits) == 10:
        return f"52{digits}"
    if len(digits) == 13 and digits.startswith('521'):
        return f"52{digits[3:]}"
    return digits


class GuestAdminForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = '__all__'

    def clean_checked_in_count(self):
        checked_in_count = self.cleaned_data.get('checked_in_count') or 0
        confirmed_companions = self.instance.confirmed_companions or 0
        if checked_in_count > confirmed_companions:
            raise forms.ValidationError(
                f'No puede ser mayor a los pases confirmados ({confirmed_companions}).'
            )
        return checked_in_count


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    form = GuestAdminForm
    list_display = ('name', 'alias', 'phone_number', 'max_companions', 'whatsapp_sent', 'is_attending', 'has_responded', 'checked_in_count', 'checked_in_at', 'whatsapp_link', 'pdf_link')
    list_editable = ('checked_in_count',)
    list_filter = ('whatsapp_sent', 'has_responded', 'is_attending', 'checked_in_at', 'is_public_rsvp', 'invitation')
    search_fields = ('name', 'alias', 'phone_number')
    readonly_fields = ('token', 'has_responded', 'is_attending', 'confirmed_companions', 'dietary_restrictions', 'checked_in_at', 'checked_in_by', 'check_in_method', 'check_in_notes', 'created_at', 'is_public_rsvp')

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

        if not guest.whatsapp_sent:
            guest.whatsapp_sent = True
            guest.save(update_fields=['whatsapp_sent', 'updated_at'])

        template = get_whatsapp_message_template(guest.invitation)
        message = render_whatsapp_message(template, guest.invitation, guest, request)
        encoded_message = urllib.parse.quote(message)
        return redirect(f'https://wa.me/{phone_number}?text={encoded_message}')

    def pdf_link(self, obj):
        url = reverse('rsvp:generate_guest_pdf', args=[obj.id])
        return format_html('<a href="{}" class="button" target="_blank">Descargar PDF</a>', url)
    pdf_link.short_description = 'Pase PDF'
    
    def get_fieldsets(self, request, obj=None):
        return (
            ('Información Principal', {
                'fields': ('invitation', 'name', 'alias', 'phone_number', 'max_companions')
            }),
            ('Opciones Avanzadas', {
                'fields': ('rsvp_deadline', 'is_public_rsvp', 'token'),
                'classes': ('collapse',)
            }),
            ('Estado de Confirmación', {
                'fields': ('has_responded', 'is_attending', 'confirmed_companions', 'dietary_restrictions'),
                'classes': ('collapse',)
            }),
            ('Recepción', {
                'fields': ('checked_in_at', 'checked_in_count', 'checked_in_by', 'check_in_method', 'check_in_notes'),
                'classes': ('collapse',)
            }),
        )


@admin.register(GuestVisit)
class GuestVisitAdmin(admin.ModelAdmin):
    list_display = ('guest', 'invitation', 'visited_at', 'ip_address')
    list_filter = ('invitation', 'visited_at')
    search_fields = ('guest__name', 'guest__alias', 'ip_address', 'user_agent')
    readonly_fields = ('guest', 'invitation', 'visited_at', 'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(GuestCheckIn)
class GuestCheckInAdmin(admin.ModelAdmin):
    list_display = ('guest', 'invitation', 'pass_count', 'method', 'checked_in_by', 'created_at')
    list_filter = ('invitation', 'method', 'created_at')
    search_fields = ('guest__name', 'guest__alias', 'checked_in_by__username')
    readonly_fields = ('guest', 'invitation', 'pass_count', 'method', 'checked_in_by', 'notes', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
