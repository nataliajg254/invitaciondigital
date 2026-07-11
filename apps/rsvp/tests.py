from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from invitations.models import Invitation
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
            phone_number='5215512345678',
            max_companions=4,
        )

    def test_invitation_administrator_can_open_guest_dashboard(self):
        self.client.login(username='manager', password='pass12345')

        response = self.client.get(reverse('invitations:dashboard', args=[self.invitation.slug]))

        self.assertEqual(response.status_code, 200)

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
        self.assertIn('https://wa.me/5215512345678', response['Location'])
        self.assertIn('http%3A//testserver/mis-xv/%3Fguest%3D', response['Location'])
