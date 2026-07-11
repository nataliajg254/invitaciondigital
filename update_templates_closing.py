import os

templates = [
    'templates/xv_natali/index.html',
    'templates/boda_elegante/index.html',
    'templates/generica/index.html',
]

closing_block = """    {% elif section.type == 'closing_message' %}
<!-- Closing Message Module -->
{% if invitation.show_closing_message and invitation.closing_message %}
<section id="closing-message" class="floral-bg text-center" style="padding: 6rem 0;">
    <div class="container">
        <div class="glass-card d-inline-block px-5 py-4" data-aos="zoom-in" style="max-width: 800px;">
            <h2 class="mb-0" style="font-family: 'Great Vibes', cursive; font-size: 3.5rem; color: var(--primary-color); font-weight: normal; line-height: 1.3;">
                {{ invitation.closing_message|linebreaksbr }}
            </h2>
        </div>
    </div>
</section>
{% endif %}
"""

for filepath in templates:
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Append before rsvp section
    target = "    {% elif section.type == 'rsvp' %}"
    
    if closing_block not in content:
        content = content.replace(target, closing_block + target)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated {filepath}")
