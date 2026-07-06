import uuid
from django.db import models

class Invitation(models.Model):
    EVENT_TYPES = [
        ('XV', 'XV Años'),
        ('BODA', 'Boda'),
        ('BAUTIZO', 'Bautizo'),
        ('CUMPLE', 'Cumpleaños'),
        ('OTRO', 'Otro Evento Social'),
    ]

    TEMPLATE_CHOICES = [
        ('xv_natali', 'Plantilla 1: Diseño Floral (Colibrí)'),
        ('boda_elegante', 'Plantilla 2: Boda Minimalista'),
        ('generica', 'Plantilla 3: Fiesta General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=150, help_text="URL amigable (ej. mis-xv-natalia)")
    
    # Event Info
    host_name = models.CharField(max_length=100, verbose_name="Nombre del Festejado(a)")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='XV')
    template_choice = models.CharField(max_length=50, choices=TEMPLATE_CHOICES, default='xv_natali')
    
    event_date = models.DateField(verbose_name="Fecha del Evento")
    event_time = models.TimeField(verbose_name="Hora del Evento")
    rsvp_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Fecha y Hora Límite de Confirmación (RSVP)")
    
    google_maps_url = models.URLField(blank=True, null=True, verbose_name="Enlace de Google Maps")
    dress_code = models.CharField(max_length=150, blank=True, null=True, verbose_name="Código de Vestimenta")
    
    HERO_POSITION_CHOICES = [
        ('center', 'Centro (Recomendado)'),
        ('top', 'Arriba'),
        ('bottom', 'Abajo'),
        ('left', 'Izquierda'),
        ('right', 'Derecha'),
    ]
    # Personalización
    custom_primary_color = models.CharField(max_length=7, blank=True, null=True, verbose_name="Color Primario (HEX)")
    custom_secondary_color = models.CharField(max_length=7, blank=True, null=True, verbose_name="Color Secundario (HEX)")
    hero_image = models.ImageField(upload_to='hero_images/', blank=True, null=True, verbose_name="Imagen Principal (Fondo)")
    hero_image_position = models.CharField(max_length=10, choices=HERO_POSITION_CHOICES, default='center', verbose_name="Alineación del Fondo")
    
    music_url = models.URLField(blank=True, null=True, verbose_name="Enlace a música (Spotify/Audio)")
    
    # Module toggles
    show_countdown = models.BooleanField(default=True, verbose_name="Mostrar Contador")
    show_location = models.BooleanField(default=True, verbose_name="Mostrar Ubicación")
    show_history = models.BooleanField(default=True, verbose_name="Mostrar Historia")
    show_gallery = models.BooleanField(default=True, verbose_name="Mostrar Galería")
    show_sponsors = models.BooleanField(default=True, verbose_name="Mostrar Padrinos")
    show_program = models.BooleanField(default=True, verbose_name="Mostrar Programa")
    show_gift_table = models.BooleanField(default=True, verbose_name="Mostrar Mesa de Regalos")
    show_music = models.BooleanField(default=True, verbose_name="Reproducir Música")
    show_rsvp = models.BooleanField(default=True, verbose_name="Mostrar RSVP")
    show_dress_code = models.BooleanField(default=True, verbose_name="Mostrar Código de Vestimenta")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invitación"
        verbose_name_plural = "Invitaciones"

    def __str__(self):
        return f"{self.host_name} - {self.get_event_type_display()}"


class ProgramEvent(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='program_events', on_delete=models.CASCADE)
    time = models.TimeField()
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'time']
        verbose_name = "Evento del Programa"
        verbose_name_plural = "Programa del Evento"

    def __str__(self):
        return f"{self.time.strftime('%H:%M')} - {self.title}"


class Sponsor(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='sponsors', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, help_text='Ej. Padrinos de Velación')

    class Meta:
        verbose_name = "Padrino"
        verbose_name_plural = "Padrinos"

    def __str__(self):
        return f"{self.role}: {self.name}"


class GiftRegistry(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='gift_registries', on_delete=models.CASCADE)
    bank_name_or_store = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco o Tienda")
    account_or_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="No. de Cuenta / Enlace")

    class Meta:
        verbose_name = "Mesa de Regalo / Cuenta"
        verbose_name_plural = "Mesa de Regalos"

    def __str__(self):
        return f"{self.bank_name_or_store} - {self.account_or_link}"
