from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from .models import Handbook
from .serializers import GETHandbookSerializer, POSTHandbookSerializer, ListHandbookSerializer
from .permissions import IsOwnerOrAdminHandbook
import fitz


# Links to all the necessaary API 
class HomePage(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            "question-api": reverse('answer_question', request=request),
            "handbook-api": reverse('list_create_handbook', request=request),
            # Make sure we have the app_name in comapnies app and we use a ":" not a "."
            "company-api": reverse('companies:list_companies', request=request)
        })


class SpecificSerializerMixin:
    """
        Applyingt his mixin will help our application choose which serializer based on the request method 
    """
    def get_serializer_class(self):
        return POSTHandbookSerializer if self.request.method in ['POST', 'PUT', 'PATCH'] else GETHandbookSerializer
    
class ListSerializerMixin:
    """
        Applying for ListCreateHandbook since we have two seperate GET vs List Serialzier 
    """
    def get_serializer_class(self):
        return POSTHandbookSerializer if self.request.method in ['POST', 'PUT', 'PATCH'] else ListHandbookSerializer

# Create your views here.
class ListCreateHandbook(ListSerializerMixin, generics.ListCreateAPIView):
    queryset = Handbook.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    # The problem here is that List overrides our permissions so we must work with filtering via requested user to ONLY SHOW that persons Handbook
    # permission_classes = [IsOwnerOrAdminHandbook]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]    # Best Option for now

    def list(self, request, *args, **kwargs):
        all_handbooks = self.get_queryset()
        serializer = self.get_serializer(all_handbooks, many=True)
        return Response(serializer.data)
    
    # When we create a handbook we want to upload that file to Pinecone
    def create(self, request): 
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Since the file is okay and our service accepted it:
            # Be sure to change file --> pdf_file because pdf_file is the field / key in the POST body 
            file = request.FILES['pdf_file']
            pdf = fitz.open(stream=file.read(), filetype='pdf')

            # Building text 
            text = ""
            for page in pdf:
                text += page.get_text()

            # Local Import for a quick Lazy Initialization 
            #
            # Be aware of top-level imports... we must use an absolute 
            from handbook_app.services.pinecone_services import injest 

            try:
                # Returned Vectorstore
                vs = injest(text)
                serializer.save()
            except Exception as e:
                
                return Response({'msg': "Error with Pinecone Injestion. File was not uploaded...", 'err': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RetrieveUpdateDestroyHandbook(SpecificSerializerMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Handbook.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'
    # For retreive this permission works perfectly
    #
    # If the requested company ISNT the ssame one on record, there's no ability to see, update or delete the record
    permission_classes = [IsOwnerOrAdminHandbook]

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
    
# Questioning 
class AskQuestion(APIView):
    """
        User would ask question for LLM Response 
    """
    def get(self, request, *args, **kwargs):
        # Endpoint to let our API users know what to add in their content body
        return Response({
            'details': "Send POST request with the key: question"
        })

    def post(self, request, *args, **kwargs):
        from handbook_app.services.pinecone_services import question
        # We need to use request.data.get not request.POST because it's only to handle forms 
        q = request.data.get('question')
        try:
            llm_answer = question(q)
            return Response({
                'answer': llm_answer
            })
        except Exception as e:
            return Response({
                'msg': "LLM Model failed to answer question",
                'err': str(e)
            })