from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from django.conf import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment='us-east-1')
_index = pc.Index(settings.PINECONE_INDEX)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# Create a function to return our index and/or pinecone client 
def get_index():
    return _index 

def get_splitter():
    return _splitter

def injest(text: str):
    pdf_splitter = get_splitter().create_documents([text])
    vectorstore = PineconeVectorStore.from_documents(
        documents=pdf_splitter,
        embedding=embeddings,
        # Make sure its index_name= not just index=
        index_name=settings.PINECONE_INDEX)
    return vectorstore