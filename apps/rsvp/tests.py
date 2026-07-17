from datetime import date, time
from io import StringIO
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from invitations.models import Invitation, InvitationWhatsAppMessage
from rsvp.admin import normalize_whatsapp_phone
from rsvp.models import Guest, GuestCheckIn, GuestVisit


class RsvpFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin',
            password='pass12345',
            is_staff=True,
            is_superuser=True,
        )
        self.manager = User.objects.create_user(username='manager', password='pass12345')
        self.other_user = User.objects.create_user(username='other', password='pass12345')
        self.hostess = User.objects.create_user(username='hostess', password='pass12345')
        self.invitation = Invitation.objects.create(
            slug='mis-xv',
            host_name='Natalia',
            event_date=date(2026, 8, 15),
            event_time=time(20, 0),
        )
        self.invitation.administrators.add(self.manager)
        self.guest = Guest.objects.create(
            invitation=self.invitation,
            name='Familia Perez',
            alias='Los Perez',
            phone_number='5215512345678',
            max_companions=4,
        )

    def test_invitation_administrator_can_open_guest_dashboard(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(reverse('invitations:dashboard', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rsvp_guest_dashboard.html')

    def test_phone_user_agent_opens_mobile_guest_dashboard(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(
            reverse('invitations:dashboard', args=[self.invitation.slug]),
            HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rsvp_mobile_guest_dashboard.html')

    def test_android_mobile_user_agent_opens_mobile_guest_dashboard(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(
            reverse('invitations:dashboard', args=[self.invitation.slug]),
            HTTP_USER_AGENT='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rsvp_mobile_guest_dashboard.html')

    def test_tablet_user_agent_keeps_desktop_guest_dashboard(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(
            reverse('invitations:dashboard', args=[self.invitation.slug]),
            HTTP_USER_AGENT='Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rsvp_guest_dashboard.html')

    def test_non_administrator_cannot_open_guest_dashboard(self):
        self.client.login(username='other', password='pass12345')

        response = self.client.get(reverse('invitations:dashboard', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 403)

    def test_role_groups_are_available(self):
        admin_group = Group.objects.get(name='Administrador de invitaciones')
        hostess_group = Group.objects.get(name='Hostess / Recepcionista')

        self.assertTrue(admin_group.permissions.filter(codename='manage_invitation_guests').exists())
        self.assertTrue(admin_group.permissions.filter(codename='manage_invitation_hostesses').exists())
        self.assertTrue(admin_group.permissions.filter(codename='view_reception_guest_list').exists())
        self.assertTrue(admin_group.permissions.filter(codename='check_in_guest').exists())
        self.assertTrue(hostess_group.permissions.filter(codename='view_reception_guest_list').exists())
        self.assertTrue(hostess_group.permissions.filter(codename='check_in_guest').exists())

    def test_hostess_can_open_reception_dashboard_only_when_assigned(self):
        self.invitation.hostesses.add(self.hostess)
        self.client.login(username='hostess', password='pass12345')

        reception_response = self.client.get(reverse('invitations:hostess_dashboard', args=[self.invitation.slug]))
        admin_response = self.client.get(reverse('invitations:dashboard', args=[self.invitation.slug]))

        self.assertEqual(reception_response.status_code, 200)
        self.assertTemplateUsed(reception_response, 'rsvp_hostess_dashboard.html')
        self.assertEqual(admin_response.status_code, 403)

    def test_unassigned_hostess_cannot_open_reception_dashboard(self):
        self.client.login(username='hostess', password='pass12345')

        response = self.client.get(reverse('invitations:hostess_dashboard', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_and_assign_hostess(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.post(
            reverse('invitations:api_hostesses_list_create', args=[self.invitation.slug]),
            data='{"username": "recepcion", "first_name": "Recepcion", "password": "temp12345"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username='recepcion')
        self.assertTrue(self.invitation.hostesses.filter(pk=user.pk).exists())
        self.assertTrue(user.groups.filter(name='Hostess / Recepcionista').exists())

    def test_hostess_can_list_reception_guests(self):
        self.invitation.hostesses.add(self.hostess)
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 2
        self.guest.save()
        self.client.login(username='hostess', password='pass12345')

        response = self.client.get(reverse('invitations:api_hostess_guests', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['name'], 'Familia Perez')

    def test_hostess_list_only_includes_confirmed_attending_guests(self):
        self.invitation.hostesses.add(self.hostess)
        Guest.objects.create(
            invitation=self.invitation,
            name='Familia Sin Confirmar',
            max_companions=2,
        )
        Guest.objects.create(
            invitation=self.invitation,
            name='Familia No Asiste',
            max_companions=2,
            has_responded=True,
            is_attending=False,
        )
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 2
        self.guest.save()
        self.client.login(username='hostess', password='pass12345')

        response = self.client.get(reverse('invitations:api_hostess_guests', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([guest['name'] for guest in response.json()], ['Familia Perez'])

    def test_hostess_can_check_in_guest_by_token(self):
        self.invitation.hostesses.add(self.hostess)
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 2
        self.guest.save()
        self.client.login(username='hostess', password='pass12345')

        response = self.client.post(
            reverse('invitations:api_hostess_check_in', args=[self.invitation.slug]),
            data=f'{{"token_or_url": "http://testserver/{self.invitation.slug}/?guest={self.guest.token}", "method": "qr", "pass_count": 2}}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.guest.refresh_from_db()
        self.assertIsNotNone(self.guest.checked_in_at)
        self.assertEqual(self.guest.checked_in_count, 2)
        self.assertEqual(self.guest.checked_in_by, self.hostess)
        self.assertEqual(self.guest.check_in_method, 'qr')
        self.assertEqual(GuestCheckIn.objects.get(guest=self.guest).pass_count, 2)

    def test_hostess_can_check_in_guest_in_partial_passes(self):
        self.invitation.hostesses.add(self.hostess)
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 2
        self.guest.save()
        self.client.login(username='hostess', password='pass12345')

        first_response = self.client.post(
            reverse('invitations:api_hostess_check_in', args=[self.invitation.slug]),
            data=f'{{"token_or_url": "{self.guest.token}", "method": "qr", "pass_count": 1}}',
            content_type='application/json',
        )
        second_response = self.client.post(
            reverse('invitations:api_hostess_check_in', args=[self.invitation.slug]),
            data=f'{{"token_or_url": "{self.guest.token}", "method": "qr", "pass_count": 1}}',
            content_type='application/json',
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.json()['guest']['checked_in_count'], 1)
        self.assertEqual(first_response.json()['guest']['remaining_passes'], 1)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.json()['guest']['checked_in_count'], 2)
        self.assertEqual(second_response.json()['guest']['remaining_passes'], 0)
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.checked_in_count, 2)
        self.assertEqual(GuestCheckIn.objects.filter(guest=self.guest).count(), 2)

    def test_hostess_check_in_without_pass_count_requests_pass_count(self):
        self.invitation.hostesses.add(self.hostess)
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 2
        self.guest.save()
        self.client.login(username='hostess', password='pass12345')

        response = self.client.post(
            reverse('invitations:api_hostess_check_in', args=[self.invitation.slug]),
            data=f'{{"token_or_url": "{self.guest.token}", "method": "qr"}}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'requires_pass_count')
        self.assertEqual(response.json()['guest']['remaining_passes'], 2)
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.checked_in_count, 0)
        self.assertFalse(GuestCheckIn.objects.filter(guest=self.guest).exists())

    def test_hostess_cannot_check_in_guest_without_confirmation(self):
        self.invitation.hostesses.add(self.hostess)
        self.client.login(username='hostess', password='pass12345')

        response = self.client.post(
            reverse('invitations:api_hostess_check_in', args=[self.invitation.slug]),
            data=f'{{"token_or_url": "{self.guest.token}", "method": "qr"}}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['status'], 'error')
        self.assertIn('no hizo la confirmación', response.json()['message'])
        self.guest.refresh_from_db()
        self.assertIsNone(self.guest.checked_in_at)

    def test_complete_check_in_does_not_overwrite_original_validation(self):
        self.invitation.hostesses.add(self.hostess)
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 2
        self.guest.checked_in_count = 2
        self.guest.checked_in_at = timezone.now()
        self.guest.checked_in_by = self.manager
        self.guest.check_in_method = 'manual'
        self.guest.save()
        self.client.login(username='hostess', password='pass12345')

        response = self.client.post(
            reverse('invitations:api_hostess_check_in', args=[self.invitation.slug]),
            data=f'{{"token_or_url": "{self.guest.token}", "method": "qr", "pass_count": 1}}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'complete')
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.checked_in_count, 2)
        self.assertEqual(self.guest.checked_in_by, self.manager)
        self.assertEqual(self.guest.check_in_method, 'manual')

    def test_guest_can_submit_rsvp_with_token(self):
        response = self.client.post(reverse('rsvp:submit', args=[self.invitation.slug]), {
            'guest_token': str(self.guest.token),
            'attending': 'true',
            'number_of_companions': '2',
            'dietary_restrictions': '',
            'comments': 'Nos vemos alla',
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['guest']['confirmed_companions'], 2)
        self.assertEqual(data['guest']['name'], 'Familia Perez')
        self.assertEqual(data['guest']['alias'], 'Los Perez')
        self.assertTrue(data['guest']['has_responded'])
        self.assertTrue(data['guest']['is_attending'])
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.has_responded)
        self.assertTrue(self.guest.is_attending)
        self.assertEqual(self.guest.confirmed_companions, 2)
        self.assertEqual(self.guest.dietary_restrictions, 'Comentarios: Nos vemos alla')

    def test_rsvp_submission_ignores_dietary_restrictions_field(self):
        response = self.client.post(reverse('rsvp:submit', args=[self.invitation.slug]), {
            'guest_token': str(self.guest.token),
            'attending': 'true',
            'number_of_companions': '2',
            'dietary_restrictions': 'Alergia al mani',
            'comments': 'Nos vemos alla',
        })

        self.assertEqual(response.status_code, 200)
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.dietary_restrictions, 'Comentarios: Nos vemos alla')

    def test_guest_can_decline_without_confirming_passes(self):
        response = self.client.post(reverse('rsvp:submit', args=[self.invitation.slug]), {
            'guest_token': str(self.guest.token),
            'attending': 'false',
            'number_of_companions': '2',
            'comments': '',
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['guest']['confirmed_companions'], 0)
        self.assertTrue(data['guest']['has_responded'])
        self.assertFalse(data['guest']['is_attending'])
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.has_responded)
        self.assertFalse(self.guest.is_attending)
        self.assertEqual(self.guest.confirmed_companions, 0)
        self.assertEqual(self.guest.dietary_restrictions, '')

    def test_public_rsvp_without_token_is_rejected(self):
        response = self.client.post(reverse('rsvp:submit', args=[self.invitation.slug]), {
            'guest_name': 'Invitado publico',
            'attending': 'true',
            'number_of_companions': '1',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Guest.objects.filter(invitation=self.invitation).count(), 1)

    def test_admin_whatsapp_link_uses_request_host(self):
        self.client.login(username='admin', password='pass12345')

        response = self.client.get(reverse('admin:rsvp_guest_whatsapp', args=[self.guest.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('https://wa.me/525512345678', response['Location'])
        self.assertIn('http%3A//testserver/mis-xv/%3Fguest%3D', response['Location'])
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.whatsapp_sent)

    def test_whatsapp_phone_adds_mexico_country_code_to_local_number(self):
        self.assertEqual(normalize_whatsapp_phone('8342742331'), '528342742331')
        self.assertEqual(normalize_whatsapp_phone('(834) 274-2331'), '528342742331')
        self.assertEqual(normalize_whatsapp_phone('5215512345678'), '525512345678')

    def test_guests_api_includes_whatsapp_sent_status(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(reverse('invitations:api_guests_list_create', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()[0]['whatsapp_sent'])

    def test_guests_api_includes_alias(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(reverse('invitations:api_guests_list_create', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['alias'], 'Los Perez')

    def test_invitation_detail_tracks_valid_guest_visit(self):
        response = self.client.get(
            reverse('invitations:detail', args=[self.invitation.slug]),
            {'guest': str(self.guest.token)},
            REMOTE_ADDR='127.0.0.1',
            HTTP_USER_AGENT='Mozilla/5.0 Test Browser',
        )

        self.assertEqual(response.status_code, 200)
        visit = GuestVisit.objects.get(guest=self.guest)
        self.assertEqual(visit.invitation, self.invitation)
        self.assertEqual(visit.ip_address, '127.0.0.1')
        self.assertEqual(visit.user_agent, 'Mozilla/5.0 Test Browser')

    def test_invitation_detail_does_not_track_missing_or_invalid_guest_visit(self):
        response_without_guest = self.client.get(reverse('invitations:detail', args=[self.invitation.slug]))
        response_with_invalid_guest = self.client.get(
            reverse('invitations:detail', args=[self.invitation.slug]),
            {'guest': str(uuid.uuid4())},
        )

        self.assertEqual(response_without_guest.status_code, 200)
        self.assertEqual(response_with_invalid_guest.status_code, 200)
        self.assertEqual(GuestVisit.objects.count(), 0)

    def test_confirmed_attending_guest_sees_qr_button(self):
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 2
        self.guest.save()

        response = self.client.get(
            reverse('invitations:detail', args=[self.invitation.slug]),
            {'guest': str(self.guest.token)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="rsvpQrButton"')
        self.assertNotContains(response, 'id="rsvpQrButton" class="btn btn-success btn-lg hover-lift px-5 py-3 d-none"')
        self.assertContains(response, f'/mis-xv/?guest={self.guest.token}')

    def test_declined_guest_does_not_see_active_qr_button(self):
        self.guest.has_responded = True
        self.guest.is_attending = False
        self.guest.confirmed_companions = 0
        self.guest.save()

        response = self.client.get(
            reverse('invitations:detail', args=[self.invitation.slug]),
            {'guest': str(self.guest.token)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="rsvpQrButton"')
        self.assertContains(response, 'd-none')

    def test_guests_api_includes_visit_count(self):
        self.client.login(username='manager', password='pass12345')
        GuestVisit.objects.create(invitation=self.invitation, guest=self.guest)
        GuestVisit.objects.create(invitation=self.invitation, guest=self.guest)

        response = self.client.get(reverse('invitations:api_guests_list_create', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['visit_count'], 2)

    def test_guest_api_can_create_and_update_alias(self):
        self.client.login(username='manager', password='pass12345')

        create_response = self.client.post(
            reverse('invitations:api_guests_list_create', args=[self.invitation.slug]),
            data='{"name": "Familia Lopez", "alias": "Lupita", "phone_number": "8341112233", "max_companions": 2}',
            content_type='application/json',
        )
        guest_id = create_response.json()['id']

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(Guest.objects.get(pk=guest_id).alias, 'Lupita')

        update_response = self.client.put(
            reverse('invitations:api_guest_detail', args=[self.invitation.slug, guest_id]),
            data='{"name": "Familia Lopez", "alias": "Los Lopez", "phone_number": "8341112233", "max_companions": 3}',
            content_type='application/json',
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(Guest.objects.get(pk=guest_id).alias, 'Los Lopez')

    def test_guest_whatsapp_sent_endpoint_marks_guest_as_sent(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.post(reverse('invitations:api_guest_whatsapp_sent', args=[self.invitation.slug, self.guest.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'whatsapp_sent': True})
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.whatsapp_sent)

    def test_whatsapp_messages_api_returns_active_messages_ordered(self):
        self.client.login(username='manager', password='pass12345')
        InvitationWhatsAppMessage.objects.create(
            invitation=self.invitation,
            title='Segundo',
            body='Hola {guest_name}',
            order=2,
        )
        InvitationWhatsAppMessage.objects.create(
            invitation=self.invitation,
            title='Primero',
            body='Hola {event_name}',
            is_default=True,
            order=1,
        )
        InvitationWhatsAppMessage.objects.create(
            invitation=self.invitation,
            title='Inactivo',
            body='No sale',
            is_active=False,
            order=0,
        )

        response = self.client.get(reverse('invitations:api_whatsapp_messages', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual([item['title'] for item in data], ['Primero', 'Segundo'])
        self.assertTrue(data[0]['is_default'])

    def test_whatsapp_messages_api_returns_fallback_without_messages(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(reverse('invitations:api_whatsapp_messages', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['title'], 'Mensaje predeterminado')
        self.assertTrue(response.json()[0]['is_default'])

    def test_whatsapp_message_preview_renders_guest_and_invitation_variables(self):
        self.client.login(username='manager', password='pass12345')
        message = InvitationWhatsAppMessage.objects.create(
            invitation=self.invitation,
            title='Con variables',
            body='{guest_name}|{guest_alias}|{event_name}|{event_date}|{event_time}|{rsvp_deadline}|{invitation_url}',
            is_default=True,
        )

        response = self.client.get(
            reverse('invitations:api_guest_whatsapp_message_preview', args=[self.invitation.slug, self.guest.pk]),
            {'message_id': message.pk},
        )

        self.assertEqual(response.status_code, 200)
        rendered = response.json()['message']
        self.assertIn('Familia Perez', rendered)
        self.assertIn('Los Perez', rendered)
        self.assertIn('Natalia', rendered)
        self.assertIn('15 de agosto de 2026', rendered)
        self.assertIn('fecha por confirmar', rendered)
        self.assertIn('http://testserver/mis-xv/?guest=', rendered)

    def test_reset_guest_status_dry_run_does_not_modify_guests(self):
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 3
        self.guest.dietary_restrictions = 'Sin gluten'
        self.guest.whatsapp_sent = True
        self.guest.save()
        output = StringIO()

        call_command('reset_guest_status', stdout=output)

        self.guest.refresh_from_db()
        self.assertTrue(self.guest.has_responded)
        self.assertTrue(self.guest.is_attending)
        self.assertEqual(self.guest.confirmed_companions, 3)
        self.assertEqual(self.guest.dietary_restrictions, 'Sin gluten')
        self.assertTrue(self.guest.whatsapp_sent)
        self.assertIn('Dry-run', output.getvalue())

    def test_reset_guest_status_with_confirm_resets_all_guests(self):
        other_invitation = Invitation.objects.create(
            slug='otra-fiesta',
            host_name='Otra Fiesta',
            event_date=date(2026, 9, 1),
            event_time=time(19, 0),
        )
        other_guest = Guest.objects.create(
            invitation=other_invitation,
            name='Familia Ruiz',
            phone_number='8341112233',
            max_companions=2,
            has_responded=True,
            is_attending=True,
            confirmed_companions=2,
            dietary_restrictions='Vegano',
            whatsapp_sent=True,
        )
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 3
        self.guest.dietary_restrictions = 'Sin gluten'
        self.guest.whatsapp_sent = True
        self.guest.save()

        call_command('reset_guest_status', '--confirm')

        self.guest.refresh_from_db()
        other_guest.refresh_from_db()
        for guest in (self.guest, other_guest):
            self.assertFalse(guest.has_responded)
            self.assertFalse(guest.is_attending)
            self.assertEqual(guest.confirmed_companions, 0)
            self.assertEqual(guest.dietary_restrictions, '')
            self.assertFalse(guest.whatsapp_sent)

    def test_reset_guest_status_with_invitation_id_resets_only_that_invitation(self):
        other_invitation = Invitation.objects.create(
            slug='otra-fiesta',
            host_name='Otra Fiesta',
            event_date=date(2026, 9, 1),
            event_time=time(19, 0),
        )
        other_guest = Guest.objects.create(
            invitation=other_invitation,
            name='Familia Ruiz',
            phone_number='8341112233',
            max_companions=2,
            has_responded=True,
            is_attending=True,
            confirmed_companions=2,
            dietary_restrictions='Vegano',
            whatsapp_sent=True,
        )
        self.guest.has_responded = True
        self.guest.is_attending = True
        self.guest.confirmed_companions = 3
        self.guest.dietary_restrictions = 'Sin gluten'
        self.guest.whatsapp_sent = True
        self.guest.save()

        call_command('reset_guest_status', '--invitation-id', str(self.invitation.pk), '--confirm')

        self.guest.refresh_from_db()
        other_guest.refresh_from_db()
        self.assertFalse(self.guest.has_responded)
        self.assertFalse(self.guest.is_attending)
        self.assertEqual(self.guest.confirmed_companions, 0)
        self.assertEqual(self.guest.dietary_restrictions, '')
        self.assertFalse(self.guest.whatsapp_sent)
        self.assertTrue(other_guest.has_responded)
        self.assertTrue(other_guest.is_attending)
        self.assertEqual(other_guest.confirmed_companions, 2)
        self.assertEqual(other_guest.dietary_restrictions, 'Vegano')
        self.assertTrue(other_guest.whatsapp_sent)

    def test_reset_guest_status_with_missing_invitation_id_raises_error(self):
        with self.assertRaises(CommandError):
            call_command('reset_guest_status', '--invitation-id', str(uuid.uuid4()), '--confirm')
