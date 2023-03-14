from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'test_user'
SLUG = 'test_slug'

INDEX_URL = reverse('posts:index')
GROUP_POSTS_URL = reverse('posts:group_posts', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
CREATE_POST_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
PROFILE_FOLLOW_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
REDIRECT_CREATE_POST_URL = f'{LOGIN_URL}?next={CREATE_POST_URL}'
PAGE_NOT_FOUND_URL = f'{INDEX_URL}unexsisting_page/'
REDIRECT_PROFILE_FOLLOW_URL = f'{LOGIN_URL}?next={PROFILE_FOLLOW_URL}'
REDIRECT_FOLLOW_URL = f'{LOGIN_URL}?next={FOLLOW_URL}'
REDIRECT_UNFOLLOW_URL = f'{LOGIN_URL}?next={UNFOLLOW_URL}'


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.user_not_author = User.objects.create(username='not_author')
        cls.group = Group.objects.create(
            title='test title',
            slug=SLUG,
            description='description test_slug'
        )
        cls.post = Post.objects.create(
            text='Test text. field-text.',
            author=cls.user,
            group=cls.group
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.REDIRECT_EDIT_POST_URL = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'

        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(user=cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user_not_author)

    def test_urls_uses_correct_template(self):
        CASES = [
            [INDEX_URL, self.guest, 'index.html'],
            [GROUP_POSTS_URL, self.guest, 'group_list.html'],
            [PROFILE_URL, self.guest, 'profile.html'],
            [self.POST_DETAIL_URL, self.guest, 'post_detail.html'],
            [self.POST_EDIT_URL, self.author, 'create_post.html'],
            [CREATE_POST_URL, self.author, 'create_post.html'],
            [PROFILE_FOLLOW_URL, self.another, 'follow.html'],
        ]
        for url, client, template in CASES:
            with self.subTest(url):
                self.assertTemplateUsed(client.get(url), f'posts/{template}')

    def test_url_exists_at_desired_location(self):
        CASES = [
            [INDEX_URL, self.guest, 200],
            [GROUP_POSTS_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [self.POST_EDIT_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.author, 200],
            [self.POST_EDIT_URL, self.another, 302],
            [CREATE_POST_URL, self.guest, 302],
            [CREATE_POST_URL, self.another, 200],
            [PAGE_NOT_FOUND_URL, self.guest, 404],
            [PROFILE_FOLLOW_URL, self.guest, 302],
            [PROFILE_FOLLOW_URL, self.another, 200],
            [FOLLOW_URL, self.guest, 302],
            [FOLLOW_URL, self.another, 302],
            [FOLLOW_URL, self.author, 302],
            [UNFOLLOW_URL, self.guest, 302],
            [UNFOLLOW_URL, self.another, 302],
            [UNFOLLOW_URL, self.author, 404],
        ]
        for url, client, status in CASES:
            with self.subTest(url=url, status=status, client=client):
                self.assertEqual(
                    client.get(url).status_code, status)

    def test_redirect(self):
        CASES = [
            [CREATE_POST_URL, self.guest, REDIRECT_CREATE_POST_URL],
            [self.POST_EDIT_URL, self.guest, self.REDIRECT_EDIT_POST_URL],
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
            [PROFILE_FOLLOW_URL, self.guest, REDIRECT_PROFILE_FOLLOW_URL],
            [FOLLOW_URL, self.guest, REDIRECT_FOLLOW_URL],
            [FOLLOW_URL, self.another, PROFILE_URL],
            [FOLLOW_URL, self.author, PROFILE_URL],
            [UNFOLLOW_URL, self.guest, REDIRECT_UNFOLLOW_URL],
            [UNFOLLOW_URL, self.another, PROFILE_URL],
        ]
        for url, client, redirect_url in CASES:
            with self.subTest(url=url, redirect=redirect_url, client=client):
                self.assertRedirects(client.get(url), redirect_url)
