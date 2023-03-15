from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from yatube.settings import MEDIA_POST_PATH

User = get_user_model()

LENGTH_TEXT = 15
FOLLOW_STR = '{0} подписан на {1}'


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор')
    description = models.TextField(
        verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        help_text='Введите текст',
        verbose_name='Текст записи')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts')
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        related_name='posts',
        help_text='Группа, к которой будет относиться запись'
    )
    image = models.ImageField(
        'Изображение',
        upload_to=MEDIA_POST_PATH,
        blank=True
    )

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

        ordering = ('-pub_date', )

    def __str__(self) -> str:
        return self.text[:LENGTH_TEXT]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Запись'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(
        'Добавить комментарий:', help_text='Введите текст.')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('-created', )

    def __str__(self) -> str:
        return self.text[:LENGTH_TEXT]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='follow_user_author_constraint'),
        )

    def __str__(self) -> str:
        return FOLLOW_STR.format(
            self.user.get_username(), self.author.get_username())

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на себя.')
