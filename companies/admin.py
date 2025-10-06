from django.contrib import admin
from .models import Quota, CompanyUser, Company

# Register your models here.
admin.site.register(Quota)
admin.site.register(Company)