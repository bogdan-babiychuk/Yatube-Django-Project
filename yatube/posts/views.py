from django.shortcuts import render, get_object_or_404, redirect
from .models import Group, Post, User, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from users.utils import paginate

RECORD: int = 10
NUMBER_30: int = 30


def index(request):
    post_list = Post.objects.all()
    page_obj = paginate(request, post_list, RECORD)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_list.all()
    page_obj = paginate(request, posts, RECORD)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    title = 'Профайл пользователя'
    author = get_object_or_404(User, username=username)
    posts = author.get_posts.all()
    count_posts = posts.count()
    page_obj = paginate(request, posts, RECORD)
    subscribe = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    context = {
        'author': author,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'title': title,
        'subscribe': subscribe}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    all_posts = post.author.get_posts
    count = all_posts.count()
    short_post = post.text[:NUMBER_30]
    title = 'Пост'
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'count': count,
        'short_post': short_post,
        'title': title,
        'form': form,
        'comments': comments,

    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/post_edit.html', context)


@login_required
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    author_posts_following = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = paginate(request, author_posts_following, RECORD)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(
        user=request.user,
        author=author
    ).exists() and request.user != author:
        Follow.objects.create(
            user=request.user,
            author=get_object_or_404(User, username=username)
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).exists()

    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:profile', username)
