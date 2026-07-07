import os

templates = [
    'apps/invitations/templates/xv_natali/index.html',
    'apps/invitations/templates/boda_elegante/index.html',
    'apps/invitations/templates/generica/index.html',
    'templates/xv_natali/index.html',
    'templates/boda_elegante/index.html',
    'templates/generica/index.html',
]

bg_style = """
    /* Fondo personalizado para secciones */
    {% if invitation.section_background_image %}
    .floral-bg, .bg-light, .bg-white, .minimal-card, .bg-dark {
        background-image: url('{{ invitation.section_background_image.url }}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-color: transparent !important;
    }
    {% endif %}
"""

separator_block = """
    {% elif section.type == 'separator' %}
<!-- Separator Image -->
<section class="separator-module" style="background-image: url('{{ section.image_url }}'); height: 50vh; background-size: cover; background-position: center; background-attachment: fixed; width: 100%; border-top: 3px solid var(--primary-color); border-bottom: 3px solid var(--primary-color);"></section>
"""

for filepath in templates:
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Custom Background Style
    if '/* Fondo personalizado para secciones */' not in content:
        content = content.replace('{% block extra_css %}\n<style>', '{% block extra_css %}\n<style>\n' + bg_style)

    # 2. Refactor loop
    content = content.replace('{% for section_name in ordered_sections %}', '{% for section in ordered_sections %}')
    content = content.replace('section_name ==', 'section.type ==')

    # 3. Add Separator Block
    if 'section.type == \'separator\'' not in content:
        # Append before {% endfor %} of the ordered_sections loop
        # Since there might be multiple {% endfor %}, we should replace the {% endfor %} that follows the last elif
        # Let's just insert it right after the first `{% if section.type == 'parents' %}` or something
        # Better: find `{% endfor %}` after the last `{% elif` but this can be tricky.
        # Actually, let's just replace `{% elif section.type == 'rsvp' %}` with the separator block and rsvp.
        content = content.replace("    {% elif section.type == 'rsvp' %}", separator_block + "    {% elif section.type == 'rsvp' %}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated {filepath}")
