from django.db import models
from .validators import validate_file_extension
from companies.models import CompanyUser
from django.utils.text import slugify

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
    
    # Created Static function for our model + view to use 
    @staticmethod
    def generate_pc_namespace(company_name:str, handbook_name:str):
        return f'company-{slugify(company_name)}-doc-{slugify(handbook_name)}'
    
    def get_pc_namespace(self):
        # Let's suglify our fields to avoid weird characters appearing in Pinecone 
        company_name = slugify(self.company.company_name)
        handbook_name = slugify(self.namespace)
        # Return the Pinecone (pc) Namespace for query and ingestion 
        ns = Handbook.generate_pc_namespace(company_name, handbook_name)
        return ns 
    
class FAQ(models.Model):
    """
        Model to synteheically generate FAQ via Openai LLM 
            - We don't use User data (privacy)
    """
    # Make sure the related_name is for THIS model: instead of related_name="handbook" it should be related_name='faq'
    handbook = models.ForeignKey(Handbook, on_delete=models.CASCADE,related_name='faq')
    question = models.CharField(max_length=255)
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.handbook.get_pc_namespace()}: {self.question[:65]}...'
