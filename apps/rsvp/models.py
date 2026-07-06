import uuid
from django.db import models
from invitations.models import Invitation

class Guest(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='guests', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name="Nombre del Invitado/Familia")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono (WhatsApp)")
    max_companions = models.PositiveIntegerField(default=0, verbose_name="Pases Asignados", help_text="Total de personas permitidas para esta familia/invitado.")
    
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_public_rsvp = models.BooleanField(default=False, verbose_name="RSVP Público")
    
    rsvp_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Fecha Límite Personalizada", help_text="Si se deja en blanco, usará la fecha límite general de la invitación.")
    
    # Estado de confirmación
    has_responded = models.BooleanField(default=False, verbose_name="¿Ya respondió?")
    is_attending = models.BooleanField(default=False, verbose_name="¿Asistirá?")
    confirmed_companions = models.PositiveIntegerField(default=0, verbose_name="Acompañantes Confirmados")
    dietary_restrictions = models.TextField(blank=True, verbose_name="Restricciones Alimenticias / Mensaje")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Invitado"
        verbose_name_plural = "Lista de Invitados"

    def __str__(self):
        status = "Pendiente"
        if self.has_responded:
            status = "Sí" if self.is_attending else "No"
        return f"{self.name} - Asiste: {status}"
