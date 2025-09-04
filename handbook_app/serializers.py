from rest_framework import serializers
from .models import Handbook

class GETHandbookSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    def get_company_name(self, handbook):
        return handbook.company.company_name
    
    class Meta:
        model = Handbook
        # Our GET request could include all the information 
        fields = (
            'id',
            'url',
            'company_name',
            'namespace',
            'pdf_file',
            'created'
        )
        extra_kwargs = {
            'url': {
                'view_name': 'retrieve_update_destroy_handbook',
                'lookup_field': 'id'
            }
        }
        

class POSTHandbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handbook
        fields = (
            'namespace',
            'pdf_file',
            'company'
        ) 

