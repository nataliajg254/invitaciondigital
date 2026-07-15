from django.core.management.base import BaseCommand, CommandError

from invitations.models import Invitation
from rsvp.models import Guest


class Command(BaseCommand):
    help = 'Restablece el estatus RSVP y WhatsApp de los invitados.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--invitation-id',
            dest='invitation_id',
            help='UUID de la invitación a restablecer. Si se omite, aplica a todas las invitaciones.',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Aplica los cambios. Si se omite, sólo muestra un resumen dry-run.',
        )

    def handle(self, *args, **options):
        invitation_id = options.get('invitation_id')
        confirm = options.get('confirm')

        guests = Guest.objects.all()
        scope = 'todas las invitaciones'

        if invitation_id:
            try:
                invitation = Invitation.objects.get(pk=invitation_id)
            except Invitation.DoesNotExist as exc:
                raise CommandError(f'No existe una invitación con id "{invitation_id}".') from exc

            guests = guests.filter(invitation=invitation)
            scope = f'invitación "{invitation.host_name}" ({invitation.pk})'

        total = guests.count()
        confirmed_count = guests.filter(has_responded=True).count()
        whatsapp_count = guests.filter(whatsapp_sent=True).count()

        self.stdout.write(f'Alcance: {scope}')
        self.stdout.write(f'Invitados encontrados: {total}')
        self.stdout.write(f'Con confirmación activa: {confirmed_count}')
        self.stdout.write(f'Con WhatsApp enviado: {whatsapp_count}')

        if total == 0:
            self.stdout.write(self.style.WARNING('No hay invitados para restablecer.'))
            return

        if not confirm:
            self.stdout.write(self.style.WARNING('Dry-run: no se modificó ningún invitado. Usa --confirm para aplicar cambios.'))
            return

        updated = guests.update(
            has_responded=False,
            is_attending=False,
            confirmed_companions=0,
            dietary_restrictions='',
            whatsapp_sent=False,
        )
        self.stdout.write(self.style.SUCCESS(f'Invitados restablecidos: {updated}'))
