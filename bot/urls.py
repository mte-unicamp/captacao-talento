# Django
from django.urls import path

# Project
from bot.views import (
    CloseCompany,
    EditCompany,
    EditHunter,
    NewCompany,
    NewHunter,
    SelectCompany,
    SelectHunter,
    success,
)


app_name = "bot"
urlpatterns = [
    path("new_company/", NewCompany.as_view(), name="new_company"),
    path("select_company/", SelectCompany.as_view(), name="select_company"),
    path("close_company/", CloseCompany.as_view(), name="close_company"),
    path("new_hunter/", NewHunter.as_view(), name="new_hunter"),
    path("select_hunter/", SelectHunter.as_view(), name="select_hunter"),
    path("edit_company/<str:name>/", EditCompany.as_view(), name="edit_company"),
    path("edit_hunter/<str:pk>/", EditHunter.as_view(), name="edit_hunter"),
    path("<str:verb>_<str:nom>/<str:name>/success/", success, name="new_company_success"),
]
