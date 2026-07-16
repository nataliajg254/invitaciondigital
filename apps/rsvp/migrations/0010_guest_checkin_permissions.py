from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp', '0009_guestvisit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='check_in_method',
            field=models.CharField(blank=True, choices=[('qr', 'QR'), ('manual', 'Manual')], max_length=10, verbose_name='Método de validación'),
        ),
        migrations.AddField(
            model_name='guest',
            name='check_in_notes',
            field=models.TextField(blank=True, verbose_name='Notas de recepción'),
        ),
        migrations.AddField(
            model_name='guest',
            name='checked_in_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de entrada'),
        ),
        migrations.AddField(
            model_name='guest',
            name='checked_in_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_in_guests', to=settings.AUTH_USER_MODEL, verbose_name='Validado por'),
        ),
        migrations.AlterModelOptions(
            name='guest',
            options={'ordering': ['name'], 'permissions': [('view_reception_guest_list', 'Puede ver lista de invitados en recepción'), ('check_in_guest', 'Puede validar entrada de invitados')], 'verbose_name': 'Invitado', 'verbose_name_plural': 'Lista de Invitados'},
        ),
    ]
