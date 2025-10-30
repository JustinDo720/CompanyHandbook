from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer 
from .models import Company, CompanyUser, Invite
from handbook_app.serializers import NestedHandbookSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Override the original UserCreate for Djoser to include company (if owner) field 
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

class NestedCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company 
        fields = (
            'id',
            'company_name',
            'url'
        )
        extra_kwargs = {
            'url': {'view_name':'companies:retrieve_company', 'lookup_field': 'company_slug'}
        }

class RetrieveCompanyUserSerializer(serializers.ModelSerializer):
    company_details = NestedCompanySerializer(many=False, source='company', read_only=True)
    class Meta:
        model = CompanyUser
        fields = (
            'id',
            'username',
            'email',
            'premium',
            'is_owner',
            'company_details'
        )

# Company Related Serializer 
class ListCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company 
        fields = (
            'id',
            'company_name',
            'company_slug',
            'owner',
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
    # Remember: The field name is the same as the related name so it should be fine to include without source
    #
    # class Handbook(models.Model):
    #   ## The rest of your Handbook fields
    #   company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='handbooks')
    handbooks = NestedHandbookSerializer(many=True, read_only=True)
    question_api_url = serializers.SerializerMethodField()

    def get_question_api_url(self, company):
        return reverse('handbook:answer_question',kwargs={'company_slug':company.company_slug}, request=self.context.get('request'))

    class Meta:
        model = Company 
        fields = (
            'id',
            'company_name',
            'company_slug',
            'is_public',
            'invite_code',
            'question_api_url',
            'owner_details',
            'handbooks',
        )

# Custom Acess + Refresh token View 
class CHandbookAuthSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        # Running the original functionality
        data = super().validate(attrs)
        
        # Including some additional information regarding the person that is requesting 
        data.update({
            'user_id': self.user.id,
            'username': self.user.username,
            'company': self.user.company.company_name if self.user.company else None,
            'company_slug': self.user.company.company_slug if self.user.company else None,
            'is_owner': self.user.is_owner,
        })

        return data 

class GetInviteSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.requested_user.username
    
    def get_company_name(self, obj):
        return obj.company.company_name
    
    class Meta:
        model = Invite 
        fields = (
            'username',
            'company_name',
            'status',
            'sent',
            'updated',
            'url',
        )
        extra_kwargs = {
            'url': {
                'view_name': 'companies:manage_invite',
                'lookup_field': 'id'
            }
        }

class PostInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = '__all__'