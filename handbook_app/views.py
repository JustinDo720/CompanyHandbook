from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response 
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Handbook
from .serializers import GETHandbookSerializer, POSTHandbookSerializer

class SpecificSerializerMixin:
    """
        Applyingt his mixin will help our application choose which serializer based on the request method 
    """
    def get_serializer_class(self):
        return POSTHandbookSerializer if self.request.method in ['POST', 'PUT', 'PATCH'] else GETHandbookSerializer

# Create your views here.
class ListCreateHandbook(SpecificSerializerMixin, generics.ListCreateAPIView):
    queryset = Handbook.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def list(self, request, *args, **kwargs):
        all_handbooks = self.get_queryset()
        serializer = self.get_serializer(all_handbooks, many=True)
        return Response(serializer.data)
    
    def create(self, request): 
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RetrieveUpdateDestroyHandbook(SpecificSerializerMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Handbook.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'

    # Don't forget to put *args and **kwargs to handle the routing...
    def get(self, request, *args, **kwargs):
        handbook = self.get_object()
        serializer = self.get_serializer(handbook, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        handbook = self.get_object()
        serializer = self.get_serializer(handbook, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request, *args, **kwargs):
        handbook = self.get_object()
        handbook.delete()
        return Response({
            "msg": "Handbook was removed successfully."
        }, status=status.HTTP_200_OK)