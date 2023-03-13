from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def page_objects(request, post, post_per_page=10):
    return Paginator(post, post_per_page).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': page_objects(
            request, Post.objects.select_related('author', 'group').all()),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'page_obj': page_objects(
            request, group.posts.select_related('author').all()),
        'group': group,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    return render(request, 'posts/profile.html', {
        'page_obj': page_objects(
            request, author.posts.select_related('group').all()),
        'author': author,
        'following': (request.user.is_authenticated
                      and request.user.username != username
                      and author.following.exists())
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(
        'author', 'group'), id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm(),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), id=post_id)
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
        })
    form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': page_objects(
            request, Post.objects.filter(
                author__following__user=request.user).select_related(
                    'author', 'group')),
    })


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(User, username=username))
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    if username != request.user.username:
        get_object_or_404(
            Follow, user=request.user, author=get_object_or_404(
                User, username=username)).delete()
    return redirect('posts:profile', username)
