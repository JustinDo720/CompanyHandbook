from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from . import views

app_name = 'companies'

urlpatterns = [
    # Override JWT endpoint for pair tokens 
    path('jwt/create/', views.CHandbookLogin.as_view(), name='jwt_create'),
    # Regular Token Pairs 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Since we put the Djoser Urls here, we can access via company/users/<djoser_endpoint>/
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    # Company
    path('all/', views.ListCompany.as_view(), name='list_companies'),
    path('all/<slug:company_slug>/', views.RetrieveCompany.as_view(), name='retrieve_company'),
    path('list/', views.ListAllPubCompanies.as_view(), name='list_pub_companies'),
    path('list/pag/', views.ListAllPubCompaniesPag.as_view(), name='list_pub_paginated_companies'),
    # Company Users (Employees)
    path('users_list/', views.ListUsers.as_view(), name='list_users'),
    path('users_list/<int:id>/', views.RetrieveUser.as_view(), name='retrieve_user'),
    # Invites to Private Companies
    path('invites/', views.ViewCreateInvite.as_view(), name='view_create_invites'),
    path('invites/search/', views.SearchInviteCode.as_view(), name='search_companies'),
    path('invites/send/', views.SendInviteCode.as_view(), name='send_invite'),
    path('invites/<int:id>/', views.ManageInvite.as_view(), name='manage_invite'),
    path('invites/users/<int:user_id>/', views.SearchPendingInv.as_view(), name='search_user_invites'),
    # Stripe Payment
    path('premium/payment/', views.UpgradeToPremium.as_view(), name='premium_payment_intent'),
    path('premium/payment/verify/', views.VerifyPremium.as_view(), name='premium_payment_verify'),
    # Lightweight Validators
    path('validate/cred/', views.VerifyUserCred.as_view(), name='validate_user_cred'),
]
