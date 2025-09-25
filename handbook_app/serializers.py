from rest_framework import serializers
from .models import Handbook, FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = (
            'question',
            'generated_on'
        )

class GETHandbookSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    company_url = serializers.HyperlinkedRelatedField(
        # Source is company referring back to Handbook.company field
        source='company',
        view_name='companies:retrieve_company',
        read_only=True,
        lookup_field='id'
    )
    # Be sure to use the source='faq' for realted_names 
    #
    # Think of it from a Handbook instance POV --> you would have handbook_instance.faq thats why source is faq
    faq_questions = FAQSerializer(source='faq', many=True, read_only=True)

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
            'created',
            'faq_questions'
        )
        extra_kwargs = {
            'url': {
                'view_name': 'handbook:retrieve_update_destroy_handbook',
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
                'view_name': 'handbook:retrieve_update_destroy_handbook',
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
                'view_name': 'handbook:retrieve_update_destroy_handbook',
                'lookup_field': 'id'
            }
        }
