from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0017_invitation_final_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='final_info_whatsapp',
            field=models.CharField(blank=True, help_text='Teléfono para solicitar más información. Incluye código de país o captura 10 dígitos de México.', max_length=20, null=True, verbose_name='WhatsApp de Información Final'),
        ),
    ]
