from django.conf import settings
from django.db import migrations, models


def copy_owner_to_administrators(apps, schema_editor):
    Invitation = apps.get_model('invitations', 'Invitation')

    for invitation in Invitation.objects.exclude(owner__isnull=True):
        invitation.administrators.add(invitation.owner_id)


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0014_invitation_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='administrators',
            field=models.ManyToManyField(
                blank=True,
                help_text='Usuarios que pueden administrar esta invitación.',
                related_name='invitations',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuarios administradores',
            ),
        ),
        migrations.RunPython(copy_owner_to_administrators, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='invitation',
            name='owner',
        ),
    ]
