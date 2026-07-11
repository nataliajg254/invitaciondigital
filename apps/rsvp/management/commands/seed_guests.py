from django.core.management.base import BaseCommand
from apps.rsvp.models import Guest
from apps.invitations.models import Invitation
import random

class Command(BaseCommand):
    help = 'Semilla para crear invitados de prueba'

    def handle(self, *args, **kwargs):
        # Asegurarnos de que haya al menos una invitación
        invitation = Invitation.objects.first()
        if not invitation:
            self.stdout.write(self.style.ERROR('No hay invitaciones creadas. Por favor crea una desde el admin primero.'))
            return

        guests_data = [
            {"name": "Familia García Pérez", "phone": "5215512345678", "passes": 4},
            {"name": "Tío Roberto y Tía Ana", "phone": "5215598765432", "passes": 2},
            {"name": "Primos Martínez", "phone": "5215545678901", "passes": 3},
            {"name": "Mejor Amiga Sofía", "phone": "5215511223344", "passes": 1},
            {"name": "Familia López", "phone": "5215599887766", "passes": 5},
        ]

        created_count = 0
        for data in guests_data:
            guest, created = Guest.objects.get_or_create(
                invitation=invitation,
                name=data["name"],
                defaults={
                    'phone_number': data["phone"],
                    'max_companions': data["passes"],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Creado: {guest.name}'))

        self.stdout.write(self.style.SUCCESS(f'¡Completado! Se crearon {created_count} invitados de prueba.'))
