# Django
from django.contrib import admin
from django.urls import path, include

# Project
import bot.views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("bot/", include("bot.urls")),
    path("", bot.views.dashboard, name="dashboard"),
    path("closed_companies/", bot.views.closed_companies, name="closed_companies"),
    path("favicon.ico", bot.views.favicon, name="favicon"),
    path("select2/", include("django_select2.urls")),
]
