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
    # Company
    path('all/', views.ListCompany.as_view(), name='list_companies'),
    path('all/<slug:company_slug>/', views.RetrieveCompany.as_view(), name='retrieve_company'),
    # Company Users (Employees)
    path('users_list/', views.ListUsers.as_view(), name='list_users'),
    path('users_list/<int:id>/', views.RetrieveUser.as_view(), name='retrieve_user'),
    # Stripe Payment
    path('premium/payment/', views.UpgradeToPremium.as_view(), name='premium_payment_intent'),
    path('premium/payment/verify/', views.VerifyPremium.as_view(), name='premium_payment_verify')
]
