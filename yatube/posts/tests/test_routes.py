from django.test import TestCase
from django.urls import reverse

from ..urls import app_name

SLUG = 'test_slug'
USERNAME = 'test_user'
POST_ID = 1

ROUTE_URLS = [
    ['/', 'index', []],
    [f'/group/{SLUG}/', 'group_posts', [SLUG]],
    [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
    [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
    ['/create/', 'post_create', []],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
    [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
    ['/follow/', 'follow_index', []],
    [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
    [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
]


class RouteURLTest(TestCase):
    def test_route_urls(self):
        for url, name_route, args in ROUTE_URLS:
            with self.subTest(name_route):
                self.assertEqual(url, reverse(
                    f'{app_name}:{name_route}', args=args))
