from django.urls import path
from bot.views import *

app_name = 'bot'
urlpatterns = [
    path('new_company/', NewCompany.as_view(), name='new_company'),
    path('select_company/', SelectCompany.as_view(), name='select_company'),
    path('close_company/', CloseCompany.as_view(), name='close_company'),
    path('new_hunter/', NewHunter.as_view(), name='new_hunter'),
    path('select_hunter/', SelectHunter.as_view(), name='select_hunter'),

    path('edit_company/<slug:name>/', EditCompany.as_view(), name='edit_company'),
    path('edit_hunter/<slug:pk>/', EditHunter.as_view(), name='edit_hunter'),

    # path('new_company/success/', NewCompanySuccess.as_view(), name='new_company_success'),
    # path('close_company/success/', CloseCompanySuccess.as_view(), name='close_company_success'),
    # path('new_hunter/success/', NewHunterSuccess.as_view(), name='new_hunter_success'),
    # path('edit_company/<str:name>/success/', EditCompanySuccess.as_view(), name='edit_company_success'),
    # path('edit_hunter/<slug:pk>/success/', EditHunterSuccess.as_view(), name='edit_hunter_success'),

]
