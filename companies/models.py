from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Our custom User Models 
class CompanyUser(AbstractUser):
    company_name = models.CharField(max_length=155, unique=True)
    company_slug = models.SlugField(max_length=155, null=True, blank=True)

    def gen_company_slug(self):
        curr_slug = slugify(self.company_name)
        new_slug = curr_slug

        cnt = 1
        while CompanyUser.objects.filter(company_slug=new_slug).exists():
            # We want to make sure this slug doesn't already exist in the database 
            new_slug = f'{curr_slug}-{cnt}'
            cnt += 1
        
        # New Slug good to go 
        return new_slug 
    
    def save(self, *args, **kwargs):
        if not self.company_slug: 
            self.company_slug = self.gen_company_slug()
        # Make sure we run super to run the parent save() method 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username