with open('apps/invitations/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_sections = """    sections = [
        ('countdown', invitation.order_countdown),
        ('ceremony', invitation.order_ceremony),
        ('location', invitation.order_location),
        ('program', invitation.order_program),
        ('parents', invitation.order_parents),
        ('sponsors', invitation.order_sponsors),
        ('gallery', invitation.order_gallery),
        ('gift_table', invitation.order_gift_table),
        ('dress_code', invitation.order_dress_code),
        ('rsvp', invitation.order_rsvp),
    ]
    sections.sort(key=lambda x: x[1])
    ordered_sections = [s[0] for s in sections]"""

new_sections = """    sections = [
        {'type': 'countdown', 'order': invitation.order_countdown},
        {'type': 'ceremony', 'order': invitation.order_ceremony},
        {'type': 'location', 'order': invitation.order_location},
        {'type': 'program', 'order': invitation.order_program},
        {'type': 'parents', 'order': invitation.order_parents},
        {'type': 'sponsors', 'order': invitation.order_sponsors},
        {'type': 'gallery', 'order': invitation.order_gallery},
        {'type': 'gift_table', 'order': invitation.order_gift_table},
        {'type': 'dress_code', 'order': invitation.order_dress_code},
        {'type': 'rsvp', 'order': invitation.order_rsvp},
    ]
    
    for sep in invitation.separator_images.all():
        if sep.image:
            sections.append({'type': 'separator', 'order': sep.order, 'image_url': sep.image.url})
            
    sections.sort(key=lambda x: x['order'])
    ordered_sections = sections"""

content = content.replace(old_sections, new_sections)

with open('apps/invitations/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
