import uuid
from django.db import models
from django.conf import settings
from invitations.models import Invitation

class Guest(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='guests', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name="Nombre del Invitado/Familia")
    alias = models.CharField(max_length=100, blank=True, null=True, verbose_name="Alias")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono (WhatsApp)")
    max_companions = models.PositiveIntegerField(default=0, verbose_name="Pases Asignados", help_text="Total de personas permitidas para esta familia/invitado.")
    
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_public_rsvp = models.BooleanField(default=False, verbose_name="RSVP Público")
    
    rsvp_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Fecha Límite Personalizada", help_text="Si se deja en blanco, usará la fecha límite general de la invitación.")
    
    # Excel y Auditoría
    sheet_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Hoja de Excel")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado por")
    whatsapp_sent = models.BooleanField(default=False, verbose_name="WhatsApp enviado")
    
    # Estado de confirmación
    has_responded = models.BooleanField(default=False, verbose_name="¿Ya respondió?")
    is_attending = models.BooleanField(default=False, verbose_name="¿Asistirá?")
    confirmed_companions = models.PositiveIntegerField(default=0, verbose_name="Acompañantes Confirmados")
    dietary_restrictions = models.TextField(blank=True, verbose_name="Restricciones Alimenticias / Mensaje")

    CHECK_IN_METHOD_CHOICES = [
        ('qr', 'QR'),
        ('manual', 'Manual'),
    ]
    checked_in_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de entrada")
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checked_in_guests',
        verbose_name="Validado por",
    )
    check_in_method = models.CharField(max_length=10, choices=CHECK_IN_METHOD_CHOICES, blank=True, verbose_name="Método de validación")
    check_in_notes = models.TextField(blank=True, verbose_name="Notas de recepción")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = ['name']
        permissions = [
            ('view_reception_guest_list', 'Puede ver lista de invitados en recepción'),
            ('check_in_guest', 'Puede validar entrada de invitados'),
        ]
        verbose_name = "Invitado"
        verbose_name_plural = "Lista de Invitados"

    def __str__(self):
        status = "Pendiente"
        if self.has_responded:
            status = "Sí" if self.is_attending else "No"
        return f"{self.name} - Asiste: {status}"


class GuestVisit(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='guest_visits', on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, related_name='visits', on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de visita")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, verbose_name="User agent")

    class Meta:
        ordering = ['-visited_at']
        verbose_name = "Visita de invitado"
        verbose_name_plural = "Visitas de invitados"

    def __str__(self):
        return f"{self.guest.name} - {self.visited_at:%Y-%m-%d %H:%M}"
