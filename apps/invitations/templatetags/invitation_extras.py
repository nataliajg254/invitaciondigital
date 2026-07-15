import re
import urllib.parse

from django import template


register = template.Library()


@register.filter
def whatsapp_info_url(phone_number):
    digits = re.sub(r'\D', '', phone_number or '')
    if len(digits) == 10:
        digits = f"52{digits}"
    elif len(digits) == 13 and digits.startswith('521'):
        digits = f"52{digits[3:]}"

    if not digits:
        return ''

    message = 'Hola, quiero mas información sobre las invitaciones digitales'
    return f"https://wa.me/{digits}?text={urllib.parse.quote(message)}"
