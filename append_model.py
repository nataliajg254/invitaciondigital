with open('apps/invitations/models.py', 'a', encoding='utf-8') as f:
    f.write("""
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
""")
