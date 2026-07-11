import os

templates = [
    'templates/boda_elegante/index.html',
    'templates/generica/index.html',
]

old_title_boda = """<h2 class="section-title" data-aos="fade-up">Acompáñanos</h2>"""
new_title_boda = """<h2 class="section-title" data-aos="fade-up">Acompáñanos</h2>
        <p class="fs-5 mt-3 mb-5 text-muted" data-aos="fade-up" data-aos-delay="100" style="max-width: 600px; margin-left: auto; margin-right: auto;">
            Te pedimos ser respetuoso con los lugares que ya hemos asignado para ti, en el pase de entrada que te hemos enviado.
        </p>"""

old_title_generica = """<h2 class="section-title text-white" data-aos="fade-up">Acompáñanos</h2>"""
new_title_generica = """<h2 class="section-title text-white" data-aos="fade-up">Acompáñanos</h2>
        <p class="fs-5 mt-3 mb-5 text-white-50" data-aos="fade-up" data-aos-delay="100" style="max-width: 600px; margin-left: auto; margin-right: auto;">
            Te pedimos ser respetuoso con los lugares que ya hemos asignado para ti, en el pase de entrada que te hemos enviado.
        </p>"""

for filepath in templates:
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'boda' in filepath:
        content = content.replace(old_title_boda, new_title_boda)
    else:
        content = content.replace(old_title_generica, new_title_generica)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated {filepath}")
