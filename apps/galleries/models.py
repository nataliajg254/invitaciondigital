from django.db import models
from invitations.models import Invitation

class MediaItem(models.Model):
    MEDIA_TYPES = [
        ('PHOTO', 'Fotografía'),
        ('VIDEO', 'Video'),
    ]

    invitation = models.ForeignKey(Invitation, related_name='gallery_items', on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='PHOTO')
    
    image = models.ImageField(upload_to='galleries/', blank=True, null=True, help_text="Sube una imagen si el tipo es Fotografía")
    video_url = models.URLField(blank=True, null=True, help_text="Enlace de YouTube/Vimeo si el tipo es Video")
    
    caption = models.CharField(max_length=200, blank=True, verbose_name="Pie de foto/video")
    order = models.PositiveIntegerField(default=0, help_text="Orden en la galería")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Elemento de Galería"
        verbose_name_plural = "Galería"

    def __str__(self):
        return f"{self.get_media_type_display()} - {self.caption or 'Sin título'}"
