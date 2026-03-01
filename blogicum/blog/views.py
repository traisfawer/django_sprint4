from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import (
    HttpRequest, HttpResponse, Http404, HttpResponseRedirect
)
from django.utils import timezone
from django.db.models import QuerySet
from typing import Any, Dict, Optional
from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserEditForm
from .utils import OnlyAuthorMixin


class IndexListView(ListView):
    """Отобразит главную страницу сайта со всеми публикациями."""

    template_name: str = 'blog/index.html'
    context_object_name: str = 'post_list'
    queryset = Post.objects.published().order_by('-pub_date')
    paginate_by: int = settings.BLOG_POSTS_PER_PAGE


class CategoryListView(ListView):
    """Отобразит страницу со всеми публикациями из выбранной категории."""

    template_name: str = 'blog/category.html'
    paginate_by: int = settings.BLOG_POSTS_PER_PAGE
    slug_url_kwarg: str = 'category_slug'

    def get_queryset(self) -> QuerySet:
        """Получит категорию и её опубликованные посты."""
        category_slug: str = self.kwargs.get(self.slug_url_kwarg)
        self.category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return self.category.posts.published().order_by('-pub_date')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавит категорию в контекст шаблона."""
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создаст новую публикацию, доступно только для
    зарегистрированных пользователей.
    """

    model = Post
    form_class = PostForm
    template_name: str = 'blog/create.html'

    def form_valid(self, form: PostForm) -> HttpResponse:
        """Валидация формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Перенаправит на страницу профиля после создания поста."""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Обновит публикацию, доступно только для автора публикации."""

    model = Post
    form_class = PostForm
    template_name: str = 'blog/create.html'
    pk_url_kwarg: str = 'post_id'

    def form_valid(self, form: PostForm) -> HttpResponse:
        """Валидация формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def handle_no_permission(self) -> HttpResponseRedirect:
        """Позволит редактировать публикацию только автору."""
        return redirect('blog:post_detail', post_id=self.get_object().id)

    def get_success_url(self) -> str:
        """Перенаправит на страницу публикации после редактирования поста."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class UserProfileView(ListView):
    """Отобразит страницу с информацией о пользователе и
    всеми его публикациями.
    """

    model = Post
    template_name: str = 'blog/profile.html'
    context_object_name: str = 'posts'
    slug_field: str = 'username'
    slug_url_kwarg: str = 'username'
    paginate_by: int = settings.BLOG_POSTS_PER_PAGE

    def get_queryset(self) -> QuerySet:
        """Получит посты, которые нужно отобразить в профиле."""
        username: str = self.kwargs.get(self.slug_url_kwarg)
        user: Optional[User] = User.objects.filter(username=username).first()
        if not user:
            raise Http404("Пользователь не найден")

        if self.request.user == user:
            queryset = Post.objects.filter(author=user).order_by('-pub_date')
        else:
            queryset = Post.objects.filter(
                author=user,
                is_published=True,
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Вернёт обновлённый словарь контекста для профиля пользователя."""
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        username: str = self.kwargs.get(self.slug_url_kwarg)
        user: Optional[User] = User.objects.filter(username=username).first()
        context['profile'] = user
        return context


@login_required
def edit_profile(request: HttpRequest) -> HttpResponse:
    """Изменит информацию о пользователе,
    доступно только владельцу аккаунта.
    """
    form: UserEditForm = UserEditForm(
        request.POST or None,
        instance=request.user
    )
    if not form.is_valid():
        return render(request, 'blog/user.html', {'form': form})
    form.save()
    return redirect('blog:profile', username=request.user.username)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Отобразит страницу с полным содержанием конкретной публикации."""
    post: Post = get_object_or_404(Post, id=post_id)

    if not post.is_published and request.user != post.author:
        raise Http404()

    if not post.category.is_published and request.user != post.author:
        raise Http404()

    if post.pub_date > timezone.now() and request.user != post.author:
        raise Http404()

    comments: QuerySet = Comment.objects.filter(post=post)
    form: CommentForm = CommentForm()

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })


@login_required
def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """Удалит публикацию, доступно только для автора публикации."""
    post: Post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    form: PostForm = PostForm(request.POST or None, instance=post)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')

    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Добавит комментарий к публикации, доступно только для
    авторизованных пользователей.
    """
    post: Post = get_object_or_404(Post, id=post_id)
    form: CommentForm = CommentForm(request.POST or None)
    comments: QuerySet = Comment.objects.filter(post=post)

    if not form.is_valid():
        return render(request, 'blog/detail.html', {
            'post': post,
            'comments': comments,
            'form': form
        })

    comment: Comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(
        request: HttpRequest,
        post_id: int,
        comment_id: int
) -> HttpResponse:
    """Изменит комментарий к публикации, доступно только для
    автора комментария.
    """
    comment: Comment = get_object_or_404(Comment, id=comment_id)
    form: CommentForm = CommentForm(request.POST or None, instance=comment)

    if request.user != comment.author:
        raise Http404

    if not form.is_valid():
        return render(
            request,
            'blog/comment.html',
            {'form': form, 'comment': comment}
        )

    form.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def delete_comment(
        request: HttpRequest,
        post_id: int,
        comment_id: int
) -> HttpResponse:
    """Удалит комментарий к публикации, доступно только для
    автора комментария.
    """
    comment: Comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)

    if not request.method == 'POST':
        return render(request, 'blog/comment.html', {'comment': comment})

    comment.delete()
    return redirect('blog:post_detail', post_id=post_id)
