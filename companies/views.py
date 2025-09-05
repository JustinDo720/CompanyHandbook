from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from .serializers import ListCompanyUserSerializer, RetrieveCompanyUserSerializer
from .models import CompanyUser

# Create your views here.
class ListCompanyUser(ListAPIView):
    queryset = CompanyUser.objects.all()
    serializer_class = ListCompanyUserSerializer

class RetrieveCompanyUser(RetrieveDestroyAPIView):
    queryset = CompanyUser.objects.all()
    serializer_class = RetrieveCompanyUserSerializer
    lookup_field = 'id'
