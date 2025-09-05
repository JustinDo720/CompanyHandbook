from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from . import views

app_name = 'companies'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Since we put the Djoser Urls here, we can access via company/users/<djoser_endpoint>/
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    # Company User 
    path('all/', views.ListCompanyUser.as_view(), name='list_companies'),
    path('all/<int:id>/', views.RetrieveCompanyUser.as_view(), name='retrieve_company')
]
