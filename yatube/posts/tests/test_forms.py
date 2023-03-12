import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User, Comment

USERNAME = 'test_user'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

CREATE_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='title group',
            slug='test_slug',
            description='description group')
        cls.group_for_edit = Group.objects.create(
            title='Title group edit',
            slug='slug_edit',
            description='Description gtoup test edit'
        )
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
        )
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.CREATE_COMMENT_URL = reverse(
            'posts:add_comment', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.client = Client()
        self.client.force_login(self.user)

    def test_create_post(self) -> None:
        form_data = {
            'text': 'Test text form',
            'group': self.post.group.id,
            'image': self.uploaded,
        }
        response = self.client.post(
            CREATE_POST_URL, data=form_data, follow=True)
        posts_after_exclude = (Post.objects.exclude(id=self.post.id))
        self.assertEqual(len(posts_after_exclude), 1)
        post = posts_after_exclude[0]
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.name, f"posts/{form_data['image'].name}")
        self.assertRedirects(response, PROFILE_URL)

    def test_edit_post(self) -> None:
        form_data = {
            'text': 'Test text edit',
            'group': self.group_for_edit.id,
            'image': SimpleUploadedFile(
                name='sma.gif',
                content=self.small_gif,
                content_type='image/gif'
            )
        }
        response = self.client.post(
            self.POST_EDIT_URL, data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.name, f"posts/{form_data['image'].name}")
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_add_comment(self):
        form_data = {
            'text': 'Test comment',
        }
        response = self.client.post(
            self.CREATE_COMMENT_URL, data=form_data, follow=True)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(response, self.POST_DETAIL_URL)
