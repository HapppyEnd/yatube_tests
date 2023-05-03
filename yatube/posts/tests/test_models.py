from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User, FOLLOW_STR
from yatube.settings import MAX_LENGHT_STR


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='user_test')
        cls.author = User.objects.create(username='author_test')
        cls.post = Post.objects.create(
            text='Test text, 123456789123456789',
            author=cls.author
        )
        cls.group = Group.objects.create(
            title='test title',
            slug='test_slug',
            description='testscription'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='test comment text'
        )
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user
        )

    def test_str_all(self):
        str_dict = {
            self.post: self.post.text[:MAX_LENGHT_STR],
            self.group: self.group.title,
            self.comment: self.comment.text[:MAX_LENGHT_STR],
            self.follow: FOLLOW_STR.format(
                self.follow.user.get_username(),
                self.follow.author.get_username())
        }
        for key, str_value in str_dict.items():
            with self.subTest(key=key):
                self.assertEqual(str_value, str(key))
