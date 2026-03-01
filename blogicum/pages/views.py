from django.shortcuts import render
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from typing import Any, Optional


class AboutView(TemplateView):
    """Создаст страницу с информацией о проекте."""

    template_name: str = 'pages/about.html'


class RulesView(TemplateView):
    """Создаст страницу с правилами проекта."""

    template_name: str = 'pages/rules.html'


def csrf_failure(
        request: HttpRequest,
        reason: str = ''
) -> HttpResponse:
    """Создаст кастомную страницу для ошибки 403."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(
        request: HttpRequest,
        exception: Optional[Exception] = None
) -> HttpResponse:
    """Создаст кастомную страницу для ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    """Создаст кастомную страницу для ошибки 500."""
    return render(request, 'pages/500.html', status=500)


@method_decorator(never_cache, name='dispatch')
class LogoutGetAllowedView(LogoutView):
    """Разрешит выход через GET-запрос."""

    http_method_names: list[str] = ['get', 'post', 'head', 'options']

    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponse:
        """Завершит сессию перед выходом."""
        request.session.flush()
        return super().dispatch(request, *args, **kwargs)
