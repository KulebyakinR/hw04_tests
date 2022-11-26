from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .utils import get_page_context

User = get_user_model()


def index(request):
    context = {
        'group_link': 'group_link',
        'author_link': 'author_link',
        'page_obj': get_page_context(Post.objects.all(), request)
    }
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
        'author_link': 'author_link',
        'group_link': 'group_link',
        'page_obj': get_page_context(group.posts.all(), request)
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {
        'author': author,
        'page_obj': get_page_context(author.posts.all(), request)
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, id=post_id)
    context = {
        "post": posts
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    post = Post(author=request.user)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': 'is_edit',
    }
    return render(
        request, 'posts/create_post.html', context)
