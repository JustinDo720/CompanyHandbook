from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer 
from .models import Company, CompanyUser
from handbook_app.serializers import NestedHandbookSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse

# Override the original UserCreate for Djoser to include our company_name field 
#
# Set this serialzier in Djoser in settings.py 
class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = CompanyUser
        fields = (
            'id',
            'username',
            'email',
            'password',
            'company'
        )

class ListCompanyUserSerializer(serializers.ModelSerializer):
    company_url = serializers.SerializerMethodField()

    def get_company_url(self, obj):
        return reverse('companies:retrieve_company', kwargs={'company_slug': obj.company.company_slug}, request=self.context.get('request')) if obj.company else None

    class Meta:
        model = CompanyUser
        fields = (
            'id',
            'url',
            'username',
            'email',
            'company',
            'company_url'
        )
        extra_kwargs = {
            'url': {'view_name': 'companies:retrieve_user', 'lookup_field': 'id'}
        }

class RetrieveCompanyUserSerializer(serializers.ModelSerializer):
    handbooks = NestedHandbookSerializer(many=True)
    question_api_url = serializers.SerializerMethodField()

    def get_question_api_url(self, company):
        # self.context.get() is where we could get the request keyword
        return reverse('handbook:answer_question',kwargs={'company':company.company_slug}, request=self.context.get('request'))

    class Meta:
        model = CompanyUser
        fields = (
            'id',
            'username',
            'email',
            'premium',
            'is_owner',
            'question_api_url',
            'handbooks'
        )

# Company Related Serializer 
class ListCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company 
        fields = (
            'id',
            'company_name',
            'company_slug',
            'is_public',
            'url'
        )
        extra_kwargs = {
            'url' : {
                'view_name': 'companies:retrieve_company', 
                'lookup_field': 'company_slug'
            }
        }

# Nested Owner 
class CompanyOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser 
        fields = (
            'id',
            'username',
            'url'
        )
        extra_kwargs = {
            'url': {
                'view_name': 'companies:retrieve_user',
                'lookup_field': 'id'
            }
        }

class RetrieveCompanySerializer(serializers.ModelSerializer):
    owner_details = CompanyOwnerSerializer(read_only=True, source='owner')

    class Meta:
        model = Company 
        fields = (
            'id',
            'company_name',
            'company_slug',
            'is_public',
            'invite_code',
            'owner_details'
        )