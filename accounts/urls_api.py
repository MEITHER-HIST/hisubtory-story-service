# accounts/urls_api.py
from django.urls import path
from . import views_api  # 명시적으로 views_api 참조

urlpatterns = [
    path("csrf/", views_api.csrf_api_view, name="csrf_api"),
    path("signup/", views_api.signup_api_view, name="signup_api"),
    path("login/", views_api.login_api_view, name="login_api"),
    path("logout/", views_api.logout_api_view, name="logout_api"),
    path("me/", views_api.me_api_view, name="me_api"),
]
