from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("telegram/", views.TelegramAuthView.as_view(), name="auth-telegram"),
    path("telegram-id/", views.TelegramIdAuthView.as_view(), name="auth-telegram-id"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("me/", views.MeView.as_view(), name="auth-me"),
]