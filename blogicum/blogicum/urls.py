from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView
from django.conf.urls.static import static
from django.conf import settings
from pages.views import LogoutGetAllowedView


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns: list = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('', include('pages.urls')),
    path(
        'auth/logout/',
        LogoutGetAllowedView.as_view(next_page='blog:index'),
        name='logout'
    ),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
