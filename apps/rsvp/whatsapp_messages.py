import re
from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

from invitations.models import InvitationWhatsAppMessage


FALLBACK_WHATSAPP_MESSAGE = (
    "¡Hola {guest_name}! Te invito cordialmente a mi evento. 🥳\n\n"
    "En el siguiente enlace puedes ver todos los detalles y confirmar tu asistencia:\n"
    "{invitation_url}\n\n"
    "¡Te espero con mucha emoción!"
)


def get_default_whatsapp_message(invitation):
    return (
        invitation.whatsapp_messages.filter(is_active=True, is_default=True).order_by('order', 'title').first()
        or invitation.whatsapp_messages.filter(is_active=True).order_by('order', 'title').first()
    )


def get_whatsapp_message_template(invitation, message_id=None):
    if message_id:
        message = invitation.whatsapp_messages.filter(pk=message_id, is_active=True).first()
        if message:
            return message.body

    default_message = get_default_whatsapp_message(invitation)
    if default_message:
        return default_message.body
    return FALLBACK_WHATSAPP_MESSAGE


def get_whatsapp_message_options(invitation):
    messages = list(invitation.whatsapp_messages.filter(is_active=True).order_by('order', 'title'))
    if messages:
        default_id = getattr(get_default_whatsapp_message(invitation), 'id', None)
        return [
            {
                'id': message.id,
                'title': message.title,
                'body': message.body,
                'is_default': message.id == default_id,
            }
            for message in messages
        ]

    return [{
        'id': None,
        'title': 'Mensaje predeterminado',
        'body': FALLBACK_WHATSAPP_MESSAGE,
        'is_default': True,
    }]


def format_date_value(value):
    if not value:
        return 'fecha por confirmar'
    if isinstance(value, datetime) and timezone.is_aware(value):
        value = timezone.localtime(value)
    return date_format(value, format='j \\d\\e F \\d\\e Y', use_l10n=True).lower()


def format_time_value(value):
    if not value:
        return 'hora por confirmar'
    return date_format(value, format='g:i A', use_l10n=True)


def build_invitation_url(request, invitation, guest):
    invitation_path = reverse('invitations:detail', args=[invitation.slug])
    return request.build_absolute_uri(f'{invitation_path}?guest={guest.token}')


def render_whatsapp_message(template, invitation, guest, request):
    deadline = guest.rsvp_deadline or invitation.rsvp_deadline
    values = {
        'guest_name': guest.name or '',
        'guest_alias': guest.alias or '',
        'event_name': invitation.host_name or '',
        'event_date': format_date_value(invitation.event_date),
        'event_time': format_time_value(invitation.event_time),
        'rsvp_deadline': format_date_value(deadline),
        'invitation_url': build_invitation_url(request, invitation, guest),
    }

    def replace_variable(match):
        return str(values.get(match.group(1), match.group(0)))

    return re.sub(r'\{([a-zA-Z_]+)\}', replace_variable, template)
