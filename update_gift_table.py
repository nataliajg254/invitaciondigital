import os

templates = [
    'templates/xv_natali/index.html',
    'templates/boda_elegante/index.html',
    'templates/generica/index.html',
]

old_code = """                    {% if gift.account_or_link %}
                    <p class="fs-5 text-muted break-word">{{ gift.account_or_link }}</p>
                    {% endif %}"""

new_code = """                    {% if gift.account_or_link %}
                        {% if 'http' in gift.account_or_link %}
                        <a href="{{ gift.account_or_link }}" target="_blank" class="btn btn-primary mt-2 px-4 py-2" style="border-radius: 20px;">Ir al enlace</a>
                        {% else %}
                        <p class="fs-5 text-muted break-word">{{ gift.account_or_link }}</p>
                        {% endif %}
                    {% endif %}"""

for filepath in templates:
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace(old_code, new_code)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated {filepath}")
