from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment


User = get_user_model()


class PostForm(forms.ModelForm):
    """Создаст форму для написания публикации."""

    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'category', 'location', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    """Создаст форму для написания комментария к публикации."""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Добавьте комментарий...'
            }),
        }


class UserEditForm(forms.ModelForm):
    """Создаст форму для редактирования информации о пользователе."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
