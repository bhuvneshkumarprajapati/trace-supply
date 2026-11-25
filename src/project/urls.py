from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from project.api import api
from project.views import dashboard

urlpatterns = [
    path("", dashboard, name="home"),
    path(
        "accounts/login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
