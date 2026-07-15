from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0016_invitationwhatsappmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='final_info_message',
            field=models.TextField(blank=True, help_text='Información adicional que aparecerá como última sección de la invitación.', null=True, verbose_name='Mensaje de Información Final'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='final_info_title',
            field=models.CharField(blank=True, default='Información', max_length=120, verbose_name='Título de Información Final'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='show_final_info',
            field=models.BooleanField(default=True, verbose_name='Mostrar Información Final'),
        ),
    ]
