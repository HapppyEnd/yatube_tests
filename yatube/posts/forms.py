from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Введите текст.',
            'group': 'Выберите группу.',
            'image': 'Выберите изображение.',
        }
        labels = {
            'text': 'Текст записи', 'group': 'Группа', 'image': 'Изображение'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        help_texts = {'text': 'Введите текст.', }
        labels = {'text': 'Добавить комментарий:', }
