from rest_framework import serializers
from .models import Handbook

class GETHandbookSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    company_url = serializers.HyperlinkedRelatedField(
        # Source is company referring back to Handbook.company field
        source='company',
        view_name='companies:retrieve_company',
        read_only=True,
        lookup_field='id'
    )

    def get_company_name(self, handbook):
        return handbook.company.company_name
    
    class Meta:
        model = Handbook
        # Our GET request could include all the information 
        fields = (
            'id',
            'url',
            'company_name',
            'company_url',
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

class ListHandbookSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    company_url = serializers.HyperlinkedRelatedField(
        # Source is company referring back to Handbook.company field
        source='company',
        view_name='companies:retrieve_company',
        read_only=True,
        lookup_field='id'
    )

    def get_company_name(self, handbook):
        return handbook.company.company_name
    
    class Meta:
        model = Handbook
        # Our GET request could include all the information (ONLY fo)
        fields = (
            'url',
            'company_name',
            'company_url',
            'namespace',
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

class NestedHandbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handbook
        fields = (
            'url',
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
