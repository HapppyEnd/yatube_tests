import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import POSTS_PER_PAGE

from ..models import Group, Post, User, Comment, Follow


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
FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR_USERNAME])


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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded)
        cls.comment = Comment.objects.create(
            author=cls.user,
            text="Comment text",
            post=cls.post
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])

    def setUp(self) -> None:
        self.client = Client()
        self.another = Client()
        self.another.force_login(self.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_context(self):
        urls = {
            INDEX_URL: 'page_obj',
            GROUP_POSTS_URL: 'page_obj',
            PROFILE_URL: 'page_obj',
            self.POST_DETAIL_URL: 'post',
        }
        for url, context_name_obj in urls.items():
            with self.subTest(url):
                if context_name_obj == 'page_obj':
                    posts = self.client.get(url).context['page_obj']
                    self.assertEqual(len(posts), 1)
                    post = posts[0]
                else:
                    post = self.client.get(url).context['post']
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

    def test_post_not_in_another_group(self):
        self.assertNotIn(
            self.post, self.client.get(GROUP_ANOTHER_URL).context['page_obj'])

    def test_correct_paginator_each_page(self):
        count_posts = Post.objects.all().count()
        self.posts_p = Post.objects.bulk_create(
            Post(
                text=f'Test text post {i}',
                author=self.user,
                group=self.group,
            ) for i in range(
                POSTS_PER_PAGE + POSTS_LAST_PAGE - count_posts)
        )
        paginator_urls = {
            INDEX_URL: POSTS_PER_PAGE,
            INDEX_URL_PAGE_TWO: POSTS_LAST_PAGE,
            GROUP_POSTS_URL: POSTS_PER_PAGE,
            GROUP_POSTS_URL_PAGE_TWO: POSTS_LAST_PAGE,
            PROFILE_URL: POSTS_PER_PAGE,
            PROFILE_URL_PAGE_TWO: POSTS_LAST_PAGE,
        }
        for url, posts_per_page in paginator_urls.items():
            with self.subTest(url):
                self.assertEqual(len(
                    self.client.get(url).context['page_obj']), posts_per_page)

    def test_comments(self):
        comments = self.client.get(self.POST_DETAIL_URL).context['comments']
        self.assertEqual(comments.count(), 1)
        comment = comments[0]
        self.assertEqual(comment.pk, self.comment.pk)
        self.assertEqual(comment.text, self.comment.text)
        self.assertEqual(comment.author, self.comment.author)
        self.assertEqual(comment.post, self.comment.post)

    def test_cache(self):
        content = self.client.get(INDEX_URL).content
        Post.objects.get(pk=self.post.pk).delete()
        content_after_delete = self.client.get(INDEX_URL).content
        self.assertEqual(content, content_after_delete)
        cache.clear()
        content_after_clear = self.client.get(INDEX_URL).content
        self.assertNotEqual(content_after_delete, content_after_clear)

    def test_follow_and_unfollow(self):
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author_user))
        response = self.another.get(FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author_user))
        self.assertRedirects(response, PROFILE_AUTHOR_URL)
        response = self.another.get(UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author_user))
        self.assertRedirects(response, PROFILE_AUTHOR_URL)

    def test_post_in_and_not_in_context_follower(self):
        post = Post.objects.create(
            text='follow text',
            author=self.author_user
        )
        Follow.objects.create(user=self.user, author=self.author_user)
        response = self.another.get(FOLLOW_INDEX_URL)
        self.assertIn(post, response.context['page_obj'])
        Follow.objects.filter(user=self.user, author=self.author_user).delete()
        response = self.another.get(FOLLOW_INDEX_URL)
        self.assertNotIn(post, response.context['page_obj'])
