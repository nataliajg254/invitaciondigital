from django.db import migrations


ADMIN_GROUP = 'Administrador de invitaciones'
HOSTESS_GROUP = 'Hostess / Recepcionista'


def create_role_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Invitation = apps.get_model('invitations', 'Invitation')
    Guest = apps.get_model('rsvp', 'Guest')

    invitation_ct = ContentType.objects.get_for_model(Invitation)
    guest_ct = ContentType.objects.get_for_model(Guest)

    permission_map = {
        'manage_invitation_guests': (invitation_ct, 'Puede administrar invitados de una invitación'),
        'manage_invitation_hostesses': (invitation_ct, 'Puede administrar hostesses de una invitación'),
        'view_reception_guest_list': (guest_ct, 'Puede ver lista de invitados en recepción'),
        'check_in_guest': (guest_ct, 'Puede validar entrada de invitados'),
    }

    permissions = {}
    for codename, (content_type, name) in permission_map.items():
        permissions[codename], _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={'name': name},
        )

    admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP)
    admin_group.permissions.add(
        permissions['manage_invitation_guests'],
        permissions['manage_invitation_hostesses'],
        permissions['view_reception_guest_list'],
        permissions['check_in_guest'],
    )

    hostess_group, _ = Group.objects.get_or_create(name=HOSTESS_GROUP)
    hostess_group.permissions.add(
        permissions['view_reception_guest_list'],
        permissions['check_in_guest'],
    )

    for invitation in Invitation.objects.prefetch_related('administrators'):
        for user in invitation.administrators.all():
            user.groups.add(admin_group)


def remove_role_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=[ADMIN_GROUP, HOSTESS_GROUP]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('invitations', '0019_invitation_hostesses_permissions'),
        ('rsvp', '0010_guest_checkin_permissions'),
    ]

    operations = [
        migrations.RunPython(create_role_groups, remove_role_groups),
    ]
