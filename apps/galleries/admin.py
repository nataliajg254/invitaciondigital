from django.contrib import admin
from django.utils.html import format_html
from .models import MediaItem

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'invitation', 'media_type', 'caption', 'order')
    list_filter = ('media_type', 'invitation')
    search_fields = ('caption', 'invitation__host_name')
    ordering = ('invitation', 'order')
    readonly_fields = ('image_preview',)
    fields = ('invitation', 'media_type', 'image', 'image_preview', 'video_url', 'caption', 'order')

    def image_preview(self, obj):
        if obj.media_type == 'PHOTO' and obj.image:
            return format_html(
                '<img src="{}" style="width: 120px; height: 80px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Preview"
