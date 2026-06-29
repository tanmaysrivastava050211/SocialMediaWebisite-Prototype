from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.timesince import timesince
from django.views.decorators.http import require_POST

from .forms import CommentForm, LoginForm, PostForm, RegisterForm
from .models import Comment, Follow, Post, UserProfile

TRENDING_TOPICS = ['#Django', '#WebDesign', '#CreatorLife', '#Photography', '#OpenSource', '#Nature']


def ensure_profile(user):
    if user.is_authenticated:
        UserProfile.objects.get_or_create(user=user)


def suggested_users(user, limit=3):
    if not user.is_authenticated:
        return User.objects.order_by('?')[:limit]
    following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
    return User.objects.exclude(id=user.id).exclude(id__in=following_ids).order_by('?')[:limit]


def serialize_post(post, user):
    return {
        'id': post.id,
        'html': render_to_string('core/_post_card.html', {'post': post, 'user': user}),
    }


@login_required
def home(request):
    ensure_profile(request.user)
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    posts_qs = Post.objects.filter(Q(author=request.user) | Q(author_id__in=following_ids)).select_related('author', 'author__profile').prefetch_related('likes', 'comments')
    paginator = Paginator(posts_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'posts': [serialize_post(post, request.user) for post in page_obj],
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    context = {
        'page_obj': page_obj,
        'post_form': PostForm(),
        'suggested_users': suggested_users(request.user),
        'right_suggestions': suggested_users(request.user),
        'trending_topics': TRENDING_TOPICS,
    }
    return render(request, 'core/home.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        ensure_profile(user)
        login(request, user)
        messages.success(request, 'Welcome to SocialSphere.')
        return redirect('home')
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ensure_profile(form.get_user())
        login(request, form.get_user())
        return redirect('home')
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User.objects.select_related('profile'), username=username)
    posts = Post.objects.filter(author=profile_user).select_related('author', 'author__profile').prefetch_related('likes', 'comments')
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
        'post_count': posts.count(),
    }
    return render(request, 'core/profile.html', context)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author', 'author__profile').prefetch_related('likes', 'comments__author__profile'), id=post_id)
    return render(request, 'core/post_detail.html', {'post': post, 'comment_form': CommentForm()})


@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'post': serialize_post(post, request.user)})
        return redirect('home')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    messages.error(request, 'Please check your post and try again.')
    return redirect('home')


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return JsonResponse({
            'success': True,
            'comment_count': post.comments.count(),
            'comment': {
                'author': request.user.username,
                'avatar': request.user.profile.avatar,
                'content': comment.content,
                'created': f'{timesince(comment.created_at)} ago',
            },
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'success': False, 'error': 'You cannot follow yourself.'}, status=400)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if created:
        following = True
    else:
        follow.delete()
        following = False
    return JsonResponse({
        'success': True,
        'following': following,
        'followers_count': target.followers.count(),
        'following_count': target.following.count(),
    })


@login_required
def explore(request):
    posts_qs = Post.objects.select_related('author', 'author__profile').prefetch_related('likes', 'comments').annotate(total_likes=Count('likes'))
    paginator = Paginator(posts_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'posts': [serialize_post(post, request.user) for post in page_obj],
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })
    return render(request, 'core/home.html', {
        'page_obj': page_obj,
        'post_form': None,
        'suggested_users': suggested_users(request.user),
        'right_suggestions': suggested_users(request.user),
        'trending_topics': TRENDING_TOPICS,
        'is_explore': True,
    })
