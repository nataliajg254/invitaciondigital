from django import forms
from django.contrib import admin
from .models import Invitation, ProgramEvent, Sponsor, GiftRegistry

class InvitationAdminForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = '__all__'
        widgets = {
            'custom_primary_color': forms.TextInput(attrs={'type': 'color', 'style': 'height: 40px; width: 60px; padding: 0; cursor: pointer;'}),
            'custom_secondary_color': forms.TextInput(attrs={'type': 'color', 'style': 'height: 40px; width: 60px; padding: 0; cursor: pointer;'}),
        }


class ProgramEventInline(admin.TabularInline):
    model = ProgramEvent
    extra = 1

class SponsorInline(admin.TabularInline):
    model = Sponsor
    extra = 1

class GiftRegistryInline(admin.TabularInline):
    model = GiftRegistry
    extra = 1

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    form = InvitationAdminForm
    list_display = ('host_name', 'event_type', 'event_date', 'slug')
    list_filter = ('event_type', 'event_date', 'template_choice')
    search_fields = ('host_name', 'slug')
    prepopulated_fields = {'slug': ('host_name',)}
    inlines = [ProgramEventInline, SponsorInline, GiftRegistryInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('host_name', 'slug', 'event_type', 'template_choice')
        }),
        ('Fecha y Hora', {
            'fields': ('event_date', 'event_time', 'rsvp_deadline')
        }),
        ('Detalles y Enlaces', {
            'fields': ('google_maps_url', 'dress_code', 'music_url')
        }),
        ('Personalización', {
            'fields': ('custom_primary_color', 'custom_secondary_color', 'hero_image', 'hero_image_position')
        }),
        ('Módulos Activos', {
            'fields': (
                'show_countdown', 'show_location', 'show_history', 
                'show_gallery', 'show_sponsors', 'show_program', 
                'show_gift_table', 'show_music', 'show_rsvp', 'show_dress_code'
            ),
            'classes': ('collapse',)
        }),
    )
