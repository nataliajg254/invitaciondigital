import os

filepath = 'apps/rsvp/admin.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add reverse import if not there
if 'from django.urls import reverse' not in content:
    content = content.replace('from django.contrib import admin', "from django.contrib import admin\nfrom django.urls import reverse")

# Update list_display
old_list = "    list_display = ('name', 'phone_number', 'max_companions', 'is_attending', 'has_responded', 'whatsapp_link')"
new_list = "    list_display = ('name', 'phone_number', 'max_companions', 'is_attending', 'has_responded', 'whatsapp_link', 'pdf_link')"
content = content.replace(old_list, new_list)

# Add pdf_link function
pdf_link_func = """    def pdf_link(self, obj):
        url = reverse('rsvp:generate_guest_pdf', args=[obj.id])
        return format_html('<a href="{}" class="button" target="_blank">Descargar PDF</a>', url)
    pdf_link.short_description = 'Pase PDF'
    
    def get_fieldsets(self, request, obj=None):
        return (
            ('Información Principal', {
                'fields': ('invitation', 'name', 'phone_number', 'max_companions')
            }),
            ('Personalización del Pase PDF', {
                'fields': ('custom_pdf_message',)
            }),
            ('Opciones Avanzadas', {
                'fields': ('rsvp_deadline', 'is_public_rsvp', 'token'),
                'classes': ('collapse',)
            }),
            ('Estado de Confirmación', {
                'fields': ('has_responded', 'is_attending', 'confirmed_companions', 'dietary_restrictions'),
                'classes': ('collapse',)
            }),
        )
"""

if 'def pdf_link' not in content:
    content = content + "\n" + pdf_link_func

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
    print("Updated admin.py")
