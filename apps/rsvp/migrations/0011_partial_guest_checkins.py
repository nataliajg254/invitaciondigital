import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invitations', '0019_invitation_hostesses_permissions'),
        ('rsvp', '0010_guest_checkin_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='checked_in_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Pases validados'),
        ),
        migrations.CreateModel(
            name='GuestCheckIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pass_count', models.PositiveIntegerField(verbose_name='Pases validados')),
                ('method', models.CharField(choices=[('qr', 'QR'), ('manual', 'Manual')], max_length=10, verbose_name='Método')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de validación')),
                ('checked_in_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guest_checkins', to=settings.AUTH_USER_MODEL, verbose_name='Validado por')),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkins', to='rsvp.guest')),
                ('invitation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_checkins', to='invitations.invitation')),
            ],
            options={
                'verbose_name': 'Entrada de invitado',
                'verbose_name_plural': 'Entradas de invitados',
                'ordering': ['-created_at'],
            },
        ),
    ]
