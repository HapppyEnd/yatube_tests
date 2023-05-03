from django.test import TestCase
from django.urls import reverse

from posts.urls import app_name

USERNAME = 'test_user'
SLUG = 'test_slug'
POST_ID = 1

URLS_ROUTES = [
    ['/', 'index', []],
    [f'/group/{SLUG}/', 'group', [SLUG]],
    [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
    [f'/{app_name}/{POST_ID}/', 'post_detail', [POST_ID]],
    ['/create/', 'post_create', []],
    [f'/{app_name}/{POST_ID}/edit/', 'post_edit', [POST_ID]],
    [f'/{app_name}/{POST_ID}/comment/', 'add_comment', [POST_ID]],
    ['/follow/', 'follow_index', []],
    [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
    [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
]


class RouteURLTest(TestCase):
    def test_route_urls(self):
        for url, url_name, args in URLS_ROUTES:
            with self.subTest(url_name):
                self.assertEqual(url, reverse(
                    f'{app_name}:{url_name}', args=args))
