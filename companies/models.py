from django.db import models
from django.contrib.auth.models import AbstractUser

# Our custom User Models 
class CompanyUser(AbstractUser):
    company_name = models.CharField(max_length=155, unique=True)


    def __str__(self):
        return self.username