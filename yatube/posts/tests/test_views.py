import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import POSTS_PER_PAGE

from ..models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POSTS_LAST_PAGE = 4
USERNAME = 'test_view_user'
AUTHOR_USERNAME = 'test_view_author'
SLUG = 'test_slug'
ANOTHER_SLUG = 'another'
INDEX_URL = reverse('posts:index')
INDEX_URL_PAGE_TWO = f'{INDEX_URL}?page=2'
GROUP_POSTS_URL = reverse('posts:group_posts', args=[SLUG])
GROUP_POSTS_URL_PAGE_TWO = f'{GROUP_POSTS_URL}?page=2'
GROUP_ANOTHER_URL = reverse('posts:group_posts', args=[ANOTHER_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_AUTHOR_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
PROFILE_URL_PAGE_TWO = f'{PROFILE_URL}?page=2'
CREATE_POST_URL = reverse('posts:post_create')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_INDEX_TWO_PAGE_URL = f'{FOLLOW_INDEX_URL}?page=2'
FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR_USERNAME])

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.author_user = User.objects.create(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title='title group',
            slug=SLUG,
            description='description group')
        cls.another_group = Group.objects.create(
            title='title another group',
            slug=ANOTHER_SLUG,
            description='description another group')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded)
        Follow.objects.create(
            user=cls.author_user,
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text="Comment text",
            post=cls.post)

        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])

        cls.client = Client()
        cls.another = Client()
        cls.another.force_login(cls.user)
        cls.follower = Client()
        cls.follower.force_login(cls.author_user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_context(self):
        CASES = [
            [INDEX_URL, self.client, 'page_obj'],
            [GROUP_POSTS_URL, self.client, 'page_obj'],
            [PROFILE_URL, self.client, 'page_obj'],
            [self.POST_DETAIL_URL, self.client, 'post'],
            [FOLLOW_INDEX_URL, self.follower, 'page_obj'],
        ]
        for url, client, context_name_obj in CASES:
            with self.subTest(url):
                if context_name_obj == 'page_obj':
                    posts = client.get(url).context['page_obj']
                    post = posts[0]
                else:
                    post = client.get(url).context['post']
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image, self.post.image)

    def test_author_in_context_profile(self):
        self.assertEqual(
            self.client.get(PROFILE_URL).context['author'], self.user)

    def test_group_in_context_group_page(self):
        group = self.client.get(GROUP_POSTS_URL).context['group']
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_post_not_in_another_line(self):
        CASES = [
            [GROUP_ANOTHER_URL, self.client],
            [FOLLOW_INDEX_URL, self.another],
        ]
        for url, client in CASES:
            with self.subTest(url):
                self.assertNotIn(
                    self.post, client.get(url).context['page_obj'])

    def test_correct_paginator_each_page(self):
        Post.objects.all().delete()
        cache.clear()
        self.posts_p = Post.objects.bulk_create(
            Post(
                text=f'Test text post {i}',
                author=self.user,
                group=self.group,
            ) for i in range(POSTS_PER_PAGE + POSTS_LAST_PAGE)
        )
        paginator_urls = {
            INDEX_URL: POSTS_PER_PAGE,
            INDEX_URL_PAGE_TWO: POSTS_LAST_PAGE,
            GROUP_POSTS_URL: POSTS_PER_PAGE,
            GROUP_POSTS_URL_PAGE_TWO: POSTS_LAST_PAGE,
            PROFILE_URL: POSTS_PER_PAGE,
            PROFILE_URL_PAGE_TWO: POSTS_LAST_PAGE,
            FOLLOW_INDEX_URL: POSTS_PER_PAGE,
            FOLLOW_INDEX_TWO_PAGE_URL: POSTS_LAST_PAGE,
        }
        for url, posts_per_page in paginator_urls.items():
            with self.subTest(url):
                self.assertEqual(len(
                    self.follower.get(
                        url).context['page_obj']), posts_per_page)

    def test_cache(self):
        content = self.client.get(INDEX_URL).content
        Post.objects.all().delete()
        content_after_delete = self.client.get(INDEX_URL).content
        self.assertEqual(content, content_after_delete)
        cache.clear()
        content_after_clear = self.client.get(INDEX_URL).content
        self.assertNotEqual(content_after_delete, content_after_clear)

    def test_follow(self):
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.author_user).exists())
        self.another.get(FOLLOW_URL)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author_user).exists())

    def test_unfollow(self):
        Follow.objects.create(user=self.user, author=self.author_user)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author_user).exists())
        self.another.get(UNFOLLOW_URL)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.author_user).exists())
