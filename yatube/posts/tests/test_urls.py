from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.urls import app_name


USERNAME = 'user-test'
SLUG = 'test_slug'

INDEX_URL = reverse(f'{app_name}:index')
GROUP_URL = reverse(f'{app_name}:group', args=[SLUG])
PROFILE_URL = reverse(f'{app_name}:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
POST_CREATE_URL = reverse(f'{app_name}:post_create')
FOLLOW_INDEX_URL = reverse(f'{app_name}:follow_index')
FOLLOW_URL = reverse(f'{app_name}:profile_follow', args=[USERNAME])
UNFOLLOW_URL = reverse(f'{app_name}:profile_unfollow', args=[USERNAME])
PAGE_NOT_FOUND_URL = '/unexisting_page/'
REDIRECT_CREATE_POST_URL = f'{LOGIN_URL}?next={POST_CREATE_URL}'
REDIRECT_FOLLOW_INDEX_URL = f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'
REDIRECT_FOLLOW_URL = f'{LOGIN_URL}?next={FOLLOW_URL}'
REDIRECT_UNFOLLOW_URL = f'{LOGIN_URL}?next={UNFOLLOW_URL}'


class PostRLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create(username=USERNAME)
        cls.another_user = User.objects.create(username='test_another')

        cls.group = Group.objects.create(
            title='title test',
            slug=SLUG,
            description='description-testription'
        )
        cls.post = Post.objects.create(
            text='Test text post',
            author=cls.user_author,
            group=cls.group
        )

        cls.POST_DETAIL_URL = reverse(
            f'{app_name}:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse(
            f'{app_name}:post_edit', args=[cls.post.id])
        cls.REDIRECT_POST_EDIT_URL = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'

        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user_author)
        cls.another = Client()
        cls.another.force_login(cls.another_user)

    def test_url_uses_correct_templates(self):
        CASES = [
            [INDEX_URL, self.guest, 'index.html'],
            [GROUP_URL, self.guest, 'group_list.html'],
            [PROFILE_URL, self.guest, 'profile.html'],
            [self.POST_DETAIL_URL, self.guest, 'post_detail.html'],
            [POST_CREATE_URL, self.author, 'post_create.html'],
            [self.POST_EDIT_URL, self.author, 'post_create.html'],
            [FOLLOW_INDEX_URL, self.another, 'follow.html'],

        ]
        for url, client, template in CASES:
            with self.subTest(url):
                self.assertTemplateUsed(
                    client.get(url), f'posts/{template}')

    def test_url_redirects(self):
        CASES = [
            [POST_CREATE_URL, self.guest, REDIRECT_CREATE_POST_URL],
            [self.POST_EDIT_URL, self.guest, self.REDIRECT_POST_EDIT_URL],
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
            [FOLLOW_INDEX_URL, self.guest, REDIRECT_FOLLOW_INDEX_URL],
            [FOLLOW_URL, self.guest, REDIRECT_FOLLOW_URL],
            [FOLLOW_URL, self.another, PROFILE_URL],
            [FOLLOW_URL, self.author, PROFILE_URL],
            [UNFOLLOW_URL, self.guest, REDIRECT_UNFOLLOW_URL],
            [UNFOLLOW_URL, self.another, PROFILE_URL]
        ]

        for url, client, redirect in CASES:
            with self.subTest(url=url, redirect=redirect, client=client):
                self.assertRedirects(client.get(url), redirect)

    def test_url_status_code(self):
        CASES = [
            [INDEX_URL, self.guest, 200],
            [GROUP_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [POST_CREATE_URL, self.guest, 302],
            [POST_CREATE_URL, self.another, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [self.POST_EDIT_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_EDIT_URL, self.author, 200],
            [PAGE_NOT_FOUND_URL, self.guest, 404],
            [FOLLOW_INDEX_URL, self.guest, 302],
            [FOLLOW_INDEX_URL, self.another, 200],
            [FOLLOW_URL, self.guest, 302],
            [FOLLOW_URL, self.another, 302],
            [FOLLOW_URL, self.author, 302],
            [UNFOLLOW_URL, self.guest, 302],
            [UNFOLLOW_URL, self.another, 302],
            [UNFOLLOW_URL, self.author, 404],

        ]

        for url, client, code_status in CASES:
            with self.subTest(url=url, status=code_status, client=client):
                self.assertEqual(client.get(url).status_code, code_status)
