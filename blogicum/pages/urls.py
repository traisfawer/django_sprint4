from django.urls import path
from . import views


app_name: str = 'pages'

urlpatterns: list = [
    path('pages/about/', views.AboutView.as_view(), name='about'),
    path('pages/rules/', views.RulesView.as_view(), name='rules'),
]
