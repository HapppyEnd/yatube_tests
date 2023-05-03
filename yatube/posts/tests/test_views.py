from django.test import Client, TestCase
from django.core.cache import cache
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User
from posts.urls import app_name
from yatube.settings import POST_PER_PAGE


USERNAME = 'test_user'
AUTHOR = 'test_author'
SLUG = 'test_slug'
ANOTHER_SLUG = 'test_another_slug'
POST_LAST_PAGE = 5


INDEX_URL = reverse(f'{app_name}:index')
INDEX_PAGE_2_URL = f'{INDEX_URL}?page=2'
GROUP_URL = reverse(f'{app_name}:group', args=[SLUG])
GROUP_ANOTHER_URL = reverse(f'{app_name}:group', args=[ANOTHER_SLUG])
GROUP_PAGE_2_URL = f'{GROUP_URL}?page=2'
PROFILE_URL = reverse(f'{app_name}:profile', args=[AUTHOR])
PROFILE_PAGE_2_URL = f'{PROFILE_URL}?page=2'
POST_CREATE_URL = reverse(f'{app_name}:post_create')
FOLLOW_INDEX_URL = reverse(f'{app_name}:follow_index')
FOLLOW_INDEX_PAGE_2_URL = f'{FOLLOW_INDEX_URL}?page=2'
FOLLOW_URL = reverse(f'{app_name}:profile_follow', args=[AUTHOR])
UNFOLLOW_URL = reverse(f'{app_name}:profile_unfollow', args=[AUTHOR])


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.another_user = User.objects.create(username=USERNAME)
        cls.author_user = User.objects.create(username=AUTHOR)

        cls.group = Group.objects.create(
            title='title test',
            slug=SLUG,
            description='description-testription'
        )
        cls.another_group = Group.objects.create(
            title='title test',
            slug=ANOTHER_SLUG,
            description='description-testription'
        )

        cls.post = Post.objects.create(
            text='Test text post',
            author=cls.author_user,
            group=cls.group
        )
        Follow.objects.create(
            user=cls.another_user,
            author=cls.author_user
        )
        cls.comment = Comment.objects.create(
            author=cls.another_user,
            text='test comment text',
            post=cls.post
        )

        cls.POST_DETAIL_URL = reverse(
            f'{app_name}:post_detail', args=[cls.post.id])

        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.author_user)
        cls.another = Client()
        cls.another.force_login(cls.another_user)

    def test_context(self):
        CASES = [
            [INDEX_URL, self.guest, 'page_obj'],
            [GROUP_URL, self.guest, 'page_obj'],
            [PROFILE_URL, self.guest, 'page_obj'],
            [self.POST_DETAIL_URL, self.guest, 'post'],
            [FOLLOW_INDEX_URL, self.another, 'page_obj'],
        ]

        for url, client, context_name in CASES:
            with self.subTest(url=url):
                response = client.get(url)
                if context_name == 'page_obj':
                    posts = response.context['page_obj']
                    self.assertEqual(len(posts), 1)
                    post = posts[0]
                else:
                    post = response.context['post']
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.author, self.post.author)

    def test_author_context(self):
        self.assertEqual(
            self.guest.get(PROFILE_URL).context['author'], self.author_user)

    def test_group_context(self):
        group = self.guest.get(GROUP_URL).context['group']
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)

    def test_post_not_in_another_place(self):
        CASES = [
            [GROUP_ANOTHER_URL, self.guest],
            [FOLLOW_INDEX_URL, self.author]
        ]
        for url, client in CASES:
            with self.subTest(url=url):
                self.assertNotIn(
                    self.post, client.get(url).context['page_obj'])

    def test_correct_paginator(self):
        Post.objects.all().delete()
        Post.objects.bulk_create(
            Post(
                text=f'test post {i}',
                author=self.author_user,
                group=self.group,
            ) for i in range(POST_PER_PAGE + POST_LAST_PAGE)
        )

        url_pages = {
            INDEX_URL: POST_PER_PAGE,
            INDEX_PAGE_2_URL: POST_LAST_PAGE,
            GROUP_URL: POST_PER_PAGE,
            GROUP_PAGE_2_URL: POST_LAST_PAGE,
            PROFILE_URL: POST_PER_PAGE,
            PROFILE_PAGE_2_URL: POST_LAST_PAGE,
            FOLLOW_INDEX_URL: POST_PER_PAGE,
            FOLLOW_INDEX_PAGE_2_URL: POST_LAST_PAGE,
        }

        for url, post_per_page in url_pages.items():
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.another.get(url).context['page_obj']),
                    post_per_page)

    def test_cache(self):
        content = self.client.get(INDEX_URL).content
        Post.objects.all().delete()
        content_after_delete = self.client.get(INDEX_URL).content
        self.assertEqual(content, content_after_delete)
        cache.clear()
        content_after_clear = self.client.get(INDEX_URL).content
        self.assertNotEqual(content_after_delete, content_after_clear)

    def test_follow(self):
        Follow.objects.all().delete()
        self.assertFalse(Follow.objects.filter(
            user=self.another_user, author=self.author_user).exists())
        self.another.get(FOLLOW_URL)
        self.assertTrue(Follow.objects.filter(
            user=self.another_user, author=self.author_user).exists())

    def test_unfollow(self):
        self.another.get(UNFOLLOW_URL)
        self.assertFalse(Follow.objects.filter(
            user=self.another_user, author=self.author_user).exists())
