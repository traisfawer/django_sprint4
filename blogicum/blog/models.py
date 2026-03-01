from django.db import models
from core.models import PublishedModel
from django.contrib.auth import get_user_model
from .querysets import PublishedPostQuerySet


TITLE_MAX_LENGTH = 256
NAME_MAX_LENGTH = 256
User = get_user_model()


class Category(PublishedModel):
    """Описывает категорию для записей в блоге.
    Категории могут быть опубликованными или неопубликованными.
    """

    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']

    def __str__(self):
        return self.title


class Location(PublishedModel):
    """Описывает местоположение, связанное с записью в блоге.
    Местоположения могут быть опубликованными или неопубликованными.
    """

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(PublishedModel):
    """Описывает публикацию."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        null=True,
        related_name='posts'
    )
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.')
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='post_images',
        blank=True
    )
    objects: (
        PublishedPostQuerySet | models.QuerySet
    ) = PublishedPostQuerySet.as_manager()

    @property
    def comment_count(self):
        """Посчитает количество комментариев у публикации."""
        return self.comments.count()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Описывает комментарий к публикации."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects: (
        PublishedPostQuerySet | models.QuerySet
    ) = PublishedPostQuerySet.as_manager()

    class Meta:
        ordering = ['created_at']
