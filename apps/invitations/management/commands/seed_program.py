from django.core.management.base import BaseCommand
from datetime import time
from invitations.models import Invitation, ProgramEvent

class Command(BaseCommand):
    help = 'Seeds the database with an itinerary from the provided image.'

    def handle(self, *args, **kwargs):
        invitation = Invitation.objects.first()
        
        if not invitation:
            self.stdout.write("No hay ninguna invitación creada. Creando una de prueba para Alexandra...")
            invitation = Invitation.objects.create(
                host_name="Alexandra",
                slug="mis-xv-alexandra",
                event_type="XV",
                template_choice="xv_natali",
                event_date="2026-08-15",
                event_time="19:00:00",
            )
        else:
            self.stdout.write(f"Usando la invitación existente: {invitation.host_name}")

        ProgramEvent.objects.filter(invitation=invitation).delete()

        events = [
            ("19:00", "RECEPCIÓN"),
            ("19:05", "ENTRADA SOLA CANCIÓN"),
            ("19:30", "INICIO SERVICIO"),
            ("19:45", "FOTOS Pastel/Familia"),
            ("20:00", "CENA"),
            ("20:30", "SEMBLANZA CANCIÓN"),
            ("20:45", "BRINDIS"),
            ("20:55", "VALS PAPÁ CANCIÓN IRIS"),
            ("21:00", "VALS MAMÁ CANCIÓN"),
            ("21:05", "VALS CHAMBELANES"),
            ("21:10", "VALS FAMILIA"),
            ("21:20", "REGALO SORPRESA"),
            ("21:30", "BAILE MODERNO"),
            ("21:35", "SHOW CHAMBELANES"),
            ("21:40", "BAILE / CABEZONES Y ROBOTS"),
            ("00:30", "FIN DE SERVICIO"),
            ("01:00", "CIERRE DE SALÓN"),
        ]

        for order, (time_str, title) in enumerate(events):
            h, m = map(int, time_str.split(':'))
            t = time(hour=h, minute=m)
            ProgramEvent.objects.create(
                invitation=invitation,
                time=t,
                title=title,
                order=order
            )
            self.stdout.write(self.style.SUCCESS(f"Agregado: {time_str} - {title}"))

        self.stdout.write(self.style.SUCCESS("¡Itinerario cargado exitosamente!"))
