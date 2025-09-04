from django.contrib import admin
from .models import Handbook
from companies.models import CompanyUser

# Register your models here.
admin.site.register(Handbook)
admin.site.register(CompanyUser)
