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
from companies.models import CompanyUser


# Links to all the necessaary API 
class HomePage(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            # "question-api": reverse('answer_question', request=request),
            "handbook-api": reverse('handbook:list_create_handbook', request=request),
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
            from handbook_app.services.pinecone_services import ingest 

            try:
                # Returned Vectorstore
                new_handbook = serializer.save()
                vs = ingest(text, new_handbook.get_pc_namespace())
                
            except Exception as e:
                
                return Response({'msg': "Error with Pinecone Ingestion. File was not uploaded...", 'err': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            from handbook_app.services.pinecone_services import update_vector, update_namespace
            # PDF_file + Namespace we Delete the current vector and create new ones 
            #
            # Just Namespace, copy over the vectors and upsert
            if 'pdf_file' in request.FILES:
                # User is sending new pdf file to replace the current 
                file = request.FILES['pdf_file']
                pdf = fitz.open(stream=file.read(), filetype='pdf')
                text = ''
                for page in pdf:
                    text += page.get_text()

                # Now that we have the new text from the new pdf:
                #
                # This will grab our namespace and DELETE the current vector while creating new vectors with that namespace
                # Runs through the classic: Splitter, Embed, Ingest 
                #
                # Double check if the namespace from our request is the same 
                new_namespace = serializer.validated_data.get('namespace', None)
                if new_namespace and new_namespace != handbook.namespace:
                    new_namespace = Handbook.generate_pc_namespace(
                        handbook.company.company_name, 
                        serializer.validated_data.get('namespace')
                    )
                elif new_namespace == handbook.namespace:
                    # Edge Case: User submitted a form with the SAME namespace 
                    new_namespace = None
                update_vector(text, handbook.get_pc_namespace(), new_namespace)
            elif 'namespace' in request.data:
                new_namespace = request.data.get('namespace')
                format_new_namespace = Handbook.generate_pc_namespace(handbook.company.company_name, new_namespace)
                update_namespace(handbook.get_pc_namespace(), format_new_namespace)
                print('Updating namespace ONLY')
            
            # Be sure to keep serializer.save() AFTER all the updates or else it consumes the file 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request, *args, **kwargs):
        try:
            handbook = self.get_object() 
            handbook.delete()

            # When we Remove a handbook in our database we also want to remove it on Pinecone
            from handbook_app.services.pinecone_services import delete_vector
            delete_vector(handbook.get_pc_namespace())
            return Response({
                "msg": "Handbook was removed successfully."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "msg": "Error removing handbook from server and/or Pinecone",
                "err": str(e)
            })
# Questioning 
class AskQuestion(APIView):
    """
        User would ask question for LLM Response 
            Updated: Company Specific --> Asking questions based on the Companies PDF 

        The idea is to ask a specific company questions based on their PDF 
    """
    permission_classes = [IsOwnerOrAdminHandbook]

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
            # We should have the company name in our URLS so we could access via **kwargs
            company = CompanyUser.objects.get(company_slug=kwargs.get('company'))
            """
            TODO: Reconfigure Question function to FILTEr via company slug (grab all the files pertaining to the company) [DONE]
            TODO: Check if this APIVIew works with kwargs.get('company') query [DONE]

            NOTE: We could filter our company for all related handbook namespaces, loop through them and query + extend our results array;
            however, for our application we want one company to have multiple BASE PDF. Our CRON job later will delete the duplicates or old variants. For now,
            let's allow mutliple submissions/files for one company.
            """
            company_handbooks_ns = [handbook.get_pc_namespace() for handbook in company.handbooks.all()]
            llm_answer = question(q, company_handbooks_ns)
            return Response({
                'answer': llm_answer
            })
        except Exception as e:
            return Response({
                'msg': "LLM Model failed to answer question",
                'err': str(e)
            })