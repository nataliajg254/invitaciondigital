with open('apps/invitations/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "{'type': 'rsvp', 'order': invitation.order_rsvp},",
    "{'type': 'rsvp', 'order': invitation.order_rsvp},\n        {'type': 'closing_message', 'order': invitation.order_closing_message},"
)

with open('apps/invitations/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
