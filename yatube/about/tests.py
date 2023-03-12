from http import HTTPStatus

from django.test import TestCase, Client


class AboutURLTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = Client()

    def test_about_urls_exists_at_desired_location(self):
        urls = [
            '/about/tech/',
            '/about/author/',
        ]

        for url in urls:
            with self.subTest(url):
                self.assertEqual(
                    self.client.get(url).status_code,
                    HTTPStatus.OK.value,
                    f'Страница по адресу {url} недоступна.'
                )
