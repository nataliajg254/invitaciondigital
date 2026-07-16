from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0018_invitation_final_info_whatsapp'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='hostesses',
            field=models.ManyToManyField(blank=True, help_text='Usuarios que pueden validar entradas en recepción para esta invitación.', related_name='hostess_invitations', to=settings.AUTH_USER_MODEL, verbose_name='Hostesses / Recepcionistas'),
        ),
        migrations.AlterModelOptions(
            name='invitation',
            options={'permissions': [('manage_invitation_guests', 'Puede administrar invitados de una invitación'), ('manage_invitation_hostesses', 'Puede administrar hostesses de una invitación')], 'verbose_name': 'Invitación', 'verbose_name_plural': 'Invitaciones'},
        ),
    ]
