from django.contrib import admin
from .models import MediaItem

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('invitation', 'media_type', 'caption', 'order')
    list_filter = ('media_type', 'invitation')
    search_fields = ('caption', 'invitation__host_name')
    ordering = ('invitation', 'order')
