import os

templates = [
    'templates/xv_natali/index.html',
    'templates/boda_elegante/index.html',
    'templates/generica/index.html',
]

old_separator = """<!-- Separator Image -->
<section class="separator-module text-center" style="width: 100%; background-color: var(--primary-color);">
    <img src="{{ section.image_url }}" alt="Separador" style="width: 100%; max-height: 80vh; object-fit: contain; display: block;">
</section>"""

new_separator = """<!-- Separator Image -->
<section class="separator-module" style="width: 100%; margin: 0; padding: 0;">
    <img src="{{ section.image_url }}" alt="Separador" style="width: 100%; height: auto; display: block;">
</section>"""

for filepath in templates:
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace(old_separator, new_separator)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated {filepath}")
