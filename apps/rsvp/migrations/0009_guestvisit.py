from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0016_invitationwhatsappmessage'),
        ('rsvp', '0008_guest_alias'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuestVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visited_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de visita')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='User agent')),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visits', to='rsvp.guest')),
                ('invitation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_visits', to='invitations.invitation')),
            ],
            options={
                'verbose_name': 'Visita de invitado',
                'verbose_name_plural': 'Visitas de invitados',
                'ordering': ['-visited_at'],
            },
        ),
    ]
