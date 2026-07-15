from django import forms
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Invitation, InvitationWhatsAppMessage, ProgramEvent, Sponsor, GiftRegistry, Parent, SeparatorImage

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


class InvitationWhatsAppMessageInline(admin.StackedInline):
    model = InvitationWhatsAppMessage
    extra = 1
    fields = ('title', 'body', 'is_default', 'is_active', 'order')


class SeparatorImageInline(admin.TabularInline):
    model = SeparatorImage
    extra = 1

class ParentInline(admin.TabularInline):
    model = Parent
    extra = 1


class InvitationAdministratorInline(admin.TabularInline):
    model = Invitation.administrators.through
    extra = 1
    verbose_name = "Invitación asignada"
    verbose_name_plural = "Invitaciones asignadas"


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    form = InvitationAdminForm
    list_display = ('host_name', 'event_type', 'event_date', 'slug', 'assigned_users')
    list_filter = ('event_type', 'event_date', 'template_choice')
    search_fields = ('host_name', 'slug')
    prepopulated_fields = {'slug': ('host_name',)}
    filter_horizontal = ('administrators',)
    inlines = [InvitationWhatsAppMessageInline, ProgramEventInline, SponsorInline, ParentInline, GiftRegistryInline, SeparatorImageInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('host_name', 'slug', 'event_type', 'template_choice', 'administrators')
        }),
        ('Fecha y Hora', {
            'fields': ('event_date', 'event_time', 'rsvp_deadline')
        }),
        ('Detalles y Enlaces (Recepción)', {
            'fields': ('location_name', 'google_maps_url', 'dress_code', 'music_url', 'music_file')
        }),
        ('Ceremonia Religiosa', {
            'fields': ('ceremony_name', 'ceremony_time', 'ceremony_google_maps_url')
        }),
        ('Personalización', {
            'fields': ('custom_primary_color', 'custom_secondary_color', 'hero_image', 'hero_image_position', 'section_background_image')
        }),
        ('Mensajes Administrables', {
            'fields': ('closing_message', 'final_info_title', 'final_info_message', 'final_info_whatsapp', 'default_pdf_message')
        }),
        ('Módulos Activos', {
            'fields': (
                'show_countdown', 'show_ceremony', 'show_location', 'show_history', 
                'show_gallery', 'show_sponsors', 'show_parents', 'show_program', 
                'show_gift_table', 'show_music', 'show_rsvp', 'show_dress_code',
                'show_closing_message', 'show_final_info'
            ),
            'classes': ('collapse',)
        }),
        ('Orden de Secciones', {
            'fields': (
                ('order_countdown', 'order_ceremony', 'order_location', 'order_program'),
                ('order_parents', 'order_sponsors', 'order_gallery'),
                ('order_gift_table', 'order_dress_code', 'order_rsvp', 'order_closing_message')
            ),
            'classes': ('collapse',)
        }),
    )

    def assigned_users(self, obj):
        users = obj.administrators.all()
        if not users:
            return "-"
        return ", ".join(user.get_username() for user in users)
    assigned_users.short_description = "Usuarios"


User = get_user_model()


class UserInvitationAdmin(BaseUserAdmin):
    inlines = BaseUserAdmin.inlines + (InvitationAdministratorInline,)


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, UserInvitationAdmin)
