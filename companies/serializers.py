from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer 
from .models import CompanyUser 
from handbook_app.serializers import NestedHandbookSerializer
from rest_framework import serializers

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
            'company_name'
        )

class ListCompanyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = (
            'id',
            'url',
            'username',
            'email',
            'company_name'
        )
        extra_kwargs = {
            'url': {'view_name': 'companies:retrieve_company', 'lookup_field': 'id'}
        }

class RetrieveCompanyUserSerializer(serializers.ModelSerializer):
    handbooks = NestedHandbookSerializer(many=True)

    class Meta:
        model = CompanyUser
        fields = (
            'id',
            'username',
            'email',
            'company_name',
            'handbooks'
        )