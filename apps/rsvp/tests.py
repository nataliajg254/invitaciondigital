from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from invitations.models import Invitation
from rsvp.admin import normalize_whatsapp_phone
from rsvp.models import Guest


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

    def test_guest_can_submit_rsvp_with_token(self):
        response = self.client.post(reverse('rsvp:submit', args=[self.invitation.slug]), {
            'guest_token': str(self.guest.token),
            'attending': 'true',
            'number_of_companions': '2',
            'dietary_restrictions': '',
            'comments': 'Nos vemos alla',
        })

        self.assertEqual(response.status_code, 200)
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.has_responded)
        self.assertTrue(self.guest.is_attending)
        self.assertEqual(self.guest.confirmed_companions, 2)

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
