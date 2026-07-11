import re
import os

ceremony_xv = """    {% elif section_name == 'ceremony' %}
<!-- Ceremony Module -->
{% if invitation.show_ceremony %}
<section id="ceremony" class="floral-bg">
    <div class="container">
        <h2 class="section-title" data-aos="fade-up">Ceremonia Religiosa</h2>
        <div class="row justify-content-center">
            <div class="col-md-8 text-center glass-card" data-aos="fade-up" data-aos-delay="100">
                <div class="row">
                    <div class="col-sm-6 mb-4 mb-sm-0 border-end">
                        <i class="bi bi-clock fs-1 mb-3" style="color: var(--primary-color);"></i>
                        <h4 class="elegant-font">Hora</h4>
                        <p class="fs-5">{{ invitation.event_date|date:"l d \de F, Y" }}</p>
                        <p class="fs-5">{{ invitation.ceremony_time|time:"h:i A" }}</p>
                    </div>
                    <div class="col-sm-6">
                        <i class="bi bi-geo-alt fs-1 mb-3" style="color: var(--primary-color);"></i>
                        <h4 class="elegant-font">Ubicación</h4>
                        <p class="fs-5">{{ invitation.ceremony_name }}</p>
                        {% if invitation.ceremony_google_maps_url %}
                        <a href="{{ invitation.ceremony_google_maps_url }}" target="_blank" class="btn btn-primary mt-2">
                            <i class="bi bi-map me-2"></i>Abrir Google Maps
                        </a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endif %}
"""

ceremony_boda = """    {% elif section_name == 'ceremony' %}
<!-- Ceremony Module -->
{% if invitation.show_ceremony %}
<section id="ceremony" class="py-5 bg-light">
    <div class="container">
        <h2 class="section-title" data-aos="fade-up">Ceremonia Religiosa</h2>
        <div class="row justify-content-center mt-5">
            <div class="col-md-8">
                <div class="minimal-card text-center" data-aos="fade-up">
                    <div class="row g-4">
                        <div class="col-sm-6 border-end-sm">
                            <i class="bi bi-clock fs-2 mb-3 text-muted"></i>
                            <h5 class="text-uppercase tracking-widest text-muted small mb-3">Hora</h5>
                            <p class="fs-5">{{ invitation.event_date|date:"l d \de F, Y" }}<br>{{ invitation.ceremony_time|time:"h:i A" }}</p>
                        </div>
                        <div class="col-sm-6">
                            <i class="bi bi-geo-alt fs-2 mb-3 text-muted"></i>
                            <h5 class="text-uppercase tracking-widest text-muted small mb-3">Ubicación</h5>
                            <p class="fs-5 mb-3">{{ invitation.ceremony_name }}</p>
                            {% if invitation.ceremony_google_maps_url %}
                            <a href="{{ invitation.ceremony_google_maps_url }}" target="_blank" class="btn btn-outline-dark btn-sm text-uppercase tracking-widest px-4">Ver Mapa</a>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endif %}
"""

ceremony_generica = """    {% elif section_name == 'ceremony' %}
<!-- Ceremony Module -->
{% if invitation.show_ceremony %}
<section id="ceremony">
    <div class="container">
        <h2 class="section-title" data-aos="fade-up">Ceremonia Religiosa</h2>
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="glass-card-dark text-center" data-aos="fade-up">
                    <div class="row g-4">
                        <div class="col-sm-6">
                            <i class="bi bi-clock fs-1 mb-3" style="color: var(--primary-color);"></i>
                            <h4 class="mb-3">Hora</h4>
                            <p class="fs-5 text-white-50">{{ invitation.event_date|date:"l d \de F, Y" }}</p>
                            <p class="fs-5 text-white">{{ invitation.ceremony_time|time:"h:i A" }}</p>
                        </div>
                        <div class="col-sm-6">
                            <i class="bi bi-geo-alt fs-1 mb-3" style="color: var(--primary-color);"></i>
                            <h4 class="mb-3">Ubicación</h4>
                            <p class="fs-5 text-white">{{ invitation.ceremony_name }}</p>
                            {% if invitation.ceremony_google_maps_url %}
                            <a href="{{ invitation.ceremony_google_maps_url }}" target="_blank" class="btn btn-primary mt-2">Ver Mapa</a>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endif %}
"""

files_to_update = {
    'templates/xv_natali/index.html': ceremony_xv,
    'templates/boda_elegante/index.html': ceremony_boda,
    'templates/generica/index.html': ceremony_generica
}

for filepath, ceremony_html in files_to_update.items():
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "section_name == 'ceremony'" not in content:
        # Insert right before location
        content = content.replace("    {% elif section_name == 'location' %}", ceremony_html + "    {% elif section_name == 'location' %}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Already updated {filepath}")
