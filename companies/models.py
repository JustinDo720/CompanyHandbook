from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid

# Our custom User Models
class Company(models.Model):
    # We used a string because our CompanyUser is defined later in the file
    owner = models.OneToOneField("CompanyUser", on_delete=models.CASCADE, related_name='owned_company')
    company_name = models.CharField(max_length=155, unique=True)
    company_slug = models.SlugField(max_length=155, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    invite_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )

    def gen_company_slug(self):
        curr_slug = slugify(self.company_name)
        new_slug = curr_slug

        cnt = 1
        while Company.objects.filter(company_slug=new_slug).exists():
            # We want to make sure this slug doesn't already exist in the database 
            new_slug = f'{curr_slug}-{cnt}'
            cnt += 1
        
        # New Slug good to go 
        return new_slug 
    
    def gen_invite_code(self):
        # UUID generates a unique identifier
        inv_code = uuid.uuid4().hex[:10].upper()
        while Company.objects.filter(invite_code=inv_code).exists():
            # Generate a new inv code (highly unlikely)
            inv_code = uuid.uuid4.hex[:10].upper()
        return inv_code
    
    def save(self, *args, **kwargs):
        if not self.company_slug: 
            self.company_slug = self.gen_company_slug()
        
        if not self.invite_code:
            self.invite_code = self.gen_invite_code()

        # Make sure we run super to run the parent save() method 
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Companies'
    
    def __str__(self):
        return self.company_name
    

class CompanyUser(AbstractUser):
    premium = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    # CAUTION: You don't want to se models.CASCADE because deleting the company will delete all users related to it... we need to set to NULL
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_users')

    def __str__(self):
        return self.username
    

class Quota(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='quota')
    amount = models.IntegerField(default=5)

    def __str__(self):
        return f'{self.company.company_name}: {self.amount} remaining...'