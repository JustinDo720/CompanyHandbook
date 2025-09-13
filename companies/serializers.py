from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer 
from .models import CompanyUser 
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
            'company_name',
            'company_slug',
            'question_api_url',
            'handbooks'
        )