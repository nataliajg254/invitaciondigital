import re

with open('apps/invitations/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Import SeparatorImage
content = content.replace(
    'from .models import Invitation, ProgramEvent, Sponsor, GiftRegistry, Parent',
    'from .models import Invitation, ProgramEvent, Sponsor, GiftRegistry, Parent, SeparatorImage'
)

# 2. Add Inline
inline_code = """
class SeparatorImageInline(admin.TabularInline):
    model = SeparatorImage
    extra = 1

"""
content = content.replace(
    'class ParentInline(admin.TabularInline):',
    inline_code + 'class ParentInline(admin.TabularInline):'
)

# 3. Register Inline
content = content.replace(
    'inlines = [ProgramEventInline, SponsorInline, ParentInline, GiftRegistryInline]',
    'inlines = [ProgramEventInline, SponsorInline, ParentInline, GiftRegistryInline, SeparatorImageInline]'
)

# 4. Add section_background_image to Personalización
content = content.replace(
    "'fields': ('custom_primary_color', 'custom_secondary_color', 'hero_image', 'hero_image_position')",
    "'fields': ('custom_primary_color', 'custom_secondary_color', 'hero_image', 'hero_image_position', 'section_background_image')"
)

with open('apps/invitations/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("admin.py updated")
