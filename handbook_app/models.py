from django.db import models
from .validators import validate_file_extension
from companies.models import CompanyUser

# Create your models here.
class Handbook(models.Model):
    namespace = models.CharField(max_length=155, unique=True)
    pdf_file = models.FileField(upload_to='handbook_files/', validators=[validate_file_extension])  # Ensure our file type is PDF only
    # We'll be using created to help with our CRON task
    created = models.DateTimeField(auto_now_add=True)

    # FK to represent a One-Many (Company-Handbook) relationship 
    company = models.ForeignKey(CompanyUser, on_delete=models.CASCADE, related_name='handbooks')

    def __str__(self):
        return self.namespace