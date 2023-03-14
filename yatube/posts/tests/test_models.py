from django.test import TestCase
from posts.models import (FOLLOW_STR, LENGTH_TEXT, Comment, Follow, Group,
                          Post, User)

USERMANE = 'test_user'
AUTHOR = 'test_atuhor'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username=USERMANE)
        cls.author = User.objects.create(username=AUTHOR)
        cls.post = Post.objects.create(
            text='Test text. Field-text.',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='Title text test for group.',
            slug='test_slug',
            description='Description text test for group.'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Text test comment'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_models_have_correct_object_names(self):
        list_class = {
            self.post: self.post.text[:LENGTH_TEXT],
            self.group: self.group.title,
            self.comment: self.comment.text[:LENGTH_TEXT],
            self.follow: FOLLOW_STR.format(
                self.follow.user.get_username(),
                self.follow.author.get_username()),
        }
        for key_class_test, str_class_value in list_class.items():
            with self.subTest(type(key_class_test).__name__):
                self.assertEqual(
                    str_class_value,
                    str(key_class_test))

    def test_verbose_name_post(self):
        field_verboses = {
            'text': 'Текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        field_help_texts = {
            'text': 'Введите текст',
            'group': 'Группа, к которой будет относиться запись',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value,
                )
