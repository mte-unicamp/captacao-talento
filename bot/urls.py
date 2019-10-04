from django.urls import path
from bot.views import *

urlpatterns = [
    path('new_company/', NewCompany.as_view(), name='new_company'),
    path('edit_company/', EditCompany.as_view(), name='edit_company'),
    path('close_company/', CloseCompany.as_view(), name='close_company'),
    path('new_hunter/', NewHunter.as_view(), name='new_hunter'),
    path('edit_hunter/', EditHunter.as_view(), name='edit_hunter'),
]
