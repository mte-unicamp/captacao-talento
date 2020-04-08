# Django
from django.contrib import admin

# Project
from .models import ClosedCompany, Company, Contractor, PostSeller, Reminder, Seller

admin.site.register(PostSeller)
admin.site.register(Seller)
admin.site.register(Contractor)
admin.site.register(Company)
admin.site.register(ClosedCompany)
admin.site.register(Reminder)
