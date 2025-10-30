from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import ListCompanyUserSerializer, RetrieveCompanyUserSerializer, ListCompanySerializer, RetrieveCompanySerializer, CHandbookAuthSerializer, GetInviteSerializer, PostInviteSerializer
from .models import CompanyUser, Company, Invite
from rest_framework.views import APIView
from companies.services.stripe_services import create_payment_intent, verify_payment
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .pagination import CompanyPagination
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
# Chaning Company User to Company
class ListCompany(ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = ListCompanySerializer
    pagination_class = CompanyPagination

    def create(self, request, *args, **kwargs):
        # Whenver we post we need to make sure we modify the owner for our user as well 
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            # Access the owner 
            owner = CompanyUser.objects.get(id=company.owner.id)
            owner.company = company
            if owner.company:
                owner.is_owner = True
                owner.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ListAllPubCompanies(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = ListCompanySerializer

    def list(self, request, *args, **kwargs):
        # Only returning public comapnies 
        pub_comp = Company.objects.filter(is_public=True)
        serializer = self.get_serializer(pub_comp, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ListAllPubCompaniesPag(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = ListCompanySerializer
    pagination_class = CompanyPagination

    def list(self, request, *args, **kwargs):
        # Only returning public comapnies 
        pub_comp = Company.objects.filter(is_public=True)

        # We need to manually apply pagination on our filtered query 
        page = self.paginate_queryset(pub_comp)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer([], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

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

# Check user cred 
def add_or_create_err(field, error_list, msg):
    """
        We need to insert error messages, but if the key doesn't exist we'll create an empty array
    """
    if field not in error_list:
        error_list[field] = []
    error_list[field].append(msg)

class VerifyUserCred(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')

        errs = {}
        if not username:
            # Unique Error 
            add_or_create_err('username', errs, "Please provide the endpoint with a username to validate")

        if not password:
            add_or_create_err('password', errs, "Please provide the endpoint with a password to validate")

        if CompanyUser.objects.filter(username=username).exists():
            add_or_create_err('username', errs, "This username is already taken. Please use a different one.")

        # Early Exit 
        if errs:
            return Response({'continue': False, 'errors': errs}, status=200)
        
        try:
            # We've already handled Username:
            #
            # 1) Unique Username 
            # 2) Blank Username 
            # 
            # Now we just need to handle the password (Don't supply the user to just simply check if the password follows our rules)
            password_validation.validate_password(password)
        except ValidationError as ve:
            # We only need to add errors for the password key 
            if 'password' not in errs:
                errs['password'] = ve.messages
            else:
                # Messages is a list so we need to make sure we extend the previous list
                errs['password'] += ve.messages

        # We'll keep the status as 200 because its our fully managed error (Expected)
        return Response({'continue': False, 'errors': errs}) if errs else Response({'continue': True})
        
# Custom Token Response 
class CHandbookLogin(TokenObtainPairView):
    serializer_class = CHandbookAuthSerializer

# Invite Views 

"""
    Handle:
        1) All Invites from a specific company slug
        2) Create an invite instance upon user post request for Invite
        3) Search a company based on their invite code
"""
class InviteSerializerMixin:
    def get_serializer_class(self):
        if self.request and self.request.method in ['POST', 'PUT', 'PATCH']:
            return PostInviteSerializer
        return GetInviteSerializer

class ViewCreateInvite(InviteSerializerMixin, ListCreateAPIView):
    queryset = Invite.objects.all()

class ManageInvite(InviteSerializerMixin, RetrieveUpdateDestroyAPIView):
    queryset = Invite.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SearchInviteCode(APIView):
    def post(self, request):
        # Searching for Company based on invite code 
        inv_code = request.data.get('invite_code')

        try:
            # Invite Codes are unique so we're only searching for one specific company 
            company = Company.objects.get(invite_code=inv_code)
            serializer = ListCompanySerializer(company, context={'request': request})
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response({'msg': "Company does not exist"}, status=status.HTTP_400_BAD_REQUEST)

class SendInviteCode(APIView):
    def post(self, request):
        # Using Invite Code to create Invite Instance
        inv_code = request.data.get('invite_code')

        # Quick end if there's no invite code provided 
        if not inv_code:
            return Response({'msg': 'Please provide an invite code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Using a try except instead of filter().exists() for better runtime 
        try:
            company = Company.objects.get(invite_code=inv_code)
        except Company.DoesNotExist:
            return Response({'msg':'Invite code does not exist. Please provide a valid one.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Creating the Invite Instance 
        invite = Invite.objects.create(
            requested_user = request.user,
            company = company
        ) 

        serializer = GetInviteSerializer(invite, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class SearchPendingInv(APIView):
    # Using GET request because we're not really creating anything
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        # Filter Invites models based on user id 
        try:
            user = CompanyUser.objects.get(id=user_id)
            has_invites = user.requested_invites.exists()
            return Response({'exists': True, 'company_name': user.requested_invites.first().company.company_name}) if has_invites else Response({'exists': False})
        except CompanyUser.DoesNotExist:
            return Response({
                'msg': "User with that ID does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)
