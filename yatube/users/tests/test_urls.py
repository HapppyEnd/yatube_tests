from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersURLTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.autorised_client = Client()
        self.autorised_client.force_login(
            User.objects.create(username='test_user'))

    def test_users_urls_exists_at_desired_location(self):
        user_urls = [
            '/auth/login/',
            '/auth/signup/',
            '/auth/logout/',
            '/auth/password_reset_form/',
        ]

        for url in user_urls:
            with self.subTest(url):
                self.assertEqual(
                    self.client.get(url).status_code,
                    HTTPStatus.OK.value,
                    f'Адрес {url} недоступен.'
                )

    def test_users_urls_exists_at_desired_location_autorised(self):
        self.assertEqual(
            self.autorised_client.get(
                reverse('users:password_change_form')).status_code,
            HTTPStatus.OK.value,
            'Адрес /auth/password_change_form/ недоступен.')
