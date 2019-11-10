from django.contrib import admin
from .models import Hunter, Seller, Contractor, Company, ClosedCompany, Reminder

admin.site.register(Seller)
admin.site.register(Contractor)
admin.site.register(Company)
admin.site.register(ClosedCompany)
admin.site.register(Reminder)
