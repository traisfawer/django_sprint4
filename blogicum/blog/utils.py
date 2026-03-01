from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):
    """Позволит видеть страницу или публикацию только автору."""

    def test_func(self) -> bool:
        """Проверит, является ли пользователь автором запроса."""
        object = self.get_object()
        return object.author == self.request.user
