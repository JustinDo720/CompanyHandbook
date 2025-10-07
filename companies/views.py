from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView, ListCreateAPIView
from .serializers import ListCompanyUserSerializer, RetrieveCompanyUserSerializer, ListCompanySerializer, RetrieveCompanySerializer
from .models import CompanyUser, Company
from rest_framework.views import APIView
from companies.services.stripe_services import create_payment_intent, verify_payment
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .pagination import CompanyPagination

# Create your views here.
# Chaning Company User to Company
class ListCompany(ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = ListCompanySerializer
    pagination_class = CompanyPagination

class RetrieveCompany(RetrieveDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = RetrieveCompanySerializer
    lookup_field = 'company_slug'

class ListUsers(ListAPIView):
    queryset = CompanyUser.objects.all()
    serializer_class = ListCompanyUserSerializer

class RetrieveUser(RetrieveDestroyAPIView):
    queryset = CompanyUser.objects.all()
    serializer_class = RetrieveCompanyUserSerializer
    lookup_field = 'id'

# Stripe API to handle Prem Users
class UpgradeToPremium(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Creating the payment intent to be verified on the frontend
            amount = 9.99    # keep in dollars --> our service function will handle the conversion   
            client_secrets = create_payment_intent(amount)
            return Response({
                'clientSecret': client_secrets
            })
        except Exception as e:
            return Response({
                'msg': 'Error Handling payment',
                'err': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyPremium(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        intent_id = request.data.get('intent_id', None)

        if not intent_id:
            return Response({
                'error': 'Please supply the intent_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        expected_prem_amount = 9.99
        prem_verification = verify_payment(intent_id, expected_prem_amount)

        # If our verification worked, we could update our User status
        if prem_verification:
            user = request.user
            # User should already be authenticated by the permission_classes guard 
            user.premium = True 
            user.save()
            return Response({
                'message': "Upgraded to Premium"
            })
        
        return Response({
            'error': "Payment not verified"
        }, status=status.HTTP_400_BAD_REQUEST)


