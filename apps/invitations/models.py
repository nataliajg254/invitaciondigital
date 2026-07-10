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
    
    location_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre del Lugar de Recepción")
    google_maps_url = models.URLField(blank=True, null=True, verbose_name="Enlace de Google Maps (Recepción)")
    
    # Ceremonia
    ceremony_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre de Iglesia/Templo (Ceremonia)")
    ceremony_time = models.TimeField(blank=True, null=True, verbose_name="Hora de la Ceremonia")
    ceremony_google_maps_url = models.URLField(blank=True, null=True, verbose_name="Enlace de Google Maps (Ceremonia)")
    
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
    section_background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True, verbose_name="Imagen de Fondo para Secciones", help_text="Opcional. Reemplaza el patrón de fondo estandar de las secciones.")
    
    music_url = models.URLField(blank=True, null=True, verbose_name="Enlace a música (Spotify/Audio)")
    music_file = models.FileField(upload_to='music/', blank=True, null=True, verbose_name="Archivo de Música MP3")
    
    # Module toggles
    show_countdown = models.BooleanField(default=True, verbose_name="Mostrar Contador")
    show_ceremony = models.BooleanField(default=False, verbose_name="Mostrar Ceremonia Religiosa")
    show_location = models.BooleanField(default=True, verbose_name="Mostrar Ubicación")
    show_history = models.BooleanField(default=True, verbose_name="Mostrar Historia")
    show_gallery = models.BooleanField(default=True, verbose_name="Mostrar Galería")
    show_sponsors = models.BooleanField(default=True, verbose_name="Mostrar Padrinos")
    show_parents = models.BooleanField(default=False, verbose_name="Mostrar Padres")
    show_program = models.BooleanField(default=True, verbose_name="Mostrar Programa")
    show_gift_table = models.BooleanField(default=True, verbose_name="Mostrar Mesa de Regalos")
    show_music = models.BooleanField(default=True, verbose_name="Reproducir Música")
    show_rsvp = models.BooleanField(default=True, verbose_name="Mostrar RSVP")
    show_closing_message = models.BooleanField(default=True, verbose_name="Mostrar Mensaje de Despedida")
    closing_message = models.TextField(blank=True, null=True, verbose_name="Mensaje de Despedida", help_text="Ej. ¡Te espero con mucho anhelo y emoción... NO FALTES!")
    default_pdf_message = models.TextField(default="Te invitamos cordialmente a celebrar este día tan especial con nosotros. Tu presencia es el mejor regalo.", verbose_name="Mensaje de Pase PDF por defecto")
    show_dress_code = models.BooleanField(default=True, verbose_name="Mostrar Código de Vestimenta")
    
    order_countdown = models.PositiveIntegerField(default=10, verbose_name="Orden Contador")
    order_ceremony = models.PositiveIntegerField(default=15, verbose_name="Orden Ceremonia")
    order_location = models.PositiveIntegerField(default=20, verbose_name="Orden Ubicación")
    order_program = models.PositiveIntegerField(default=30, verbose_name="Orden Programa")
    order_parents = models.PositiveIntegerField(default=40, verbose_name="Orden Padres")
    order_sponsors = models.PositiveIntegerField(default=50, verbose_name="Orden Padrinos")
    order_gallery = models.PositiveIntegerField(default=60, verbose_name="Orden Galería")
    order_gift_table = models.PositiveIntegerField(default=70, verbose_name="Orden Mesa de Regalos")
    order_dress_code = models.PositiveIntegerField(default=80, verbose_name="Orden Código de Vestimenta")
    order_rsvp = models.PositiveIntegerField(default=90, verbose_name="Orden Confirmación (RSVP)")
    order_closing_message = models.PositiveIntegerField(default=100, verbose_name="Orden Mensaje de Despedida")

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

class Parent(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='parents', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, help_text='Ej. Padres de la Novia, Padres del Novio')

    class Meta:
        verbose_name = "Padre/Madre"
        verbose_name_plural = "Padres"

    def __str__(self):
        return f"{self.role}: {self.name}"

class SeparatorImage(models.Model):
    invitation = models.ForeignKey(Invitation, related_name='separator_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='separators/', verbose_name="Imagen Separadora")
    order = models.PositiveIntegerField(default=25, verbose_name="Orden (Posición)")

    class Meta:
        ordering = ['order']
        verbose_name = "Imagen Separadora"
        verbose_name_plural = "Imágenes Separadoras"

    def __str__(self):
        return f"Separador {self.order} - {self.invitation.host_name}"
