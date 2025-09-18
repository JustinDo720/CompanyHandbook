from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from django.conf import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment='us-east-1')
_index = pc.Index(settings.PINECONE_INDEX)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)
_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# Create a function to return our index and/or pinecone client 
def get_index():
    return _index 

def get_splitter():
    return _splitter

def get_pinecone():
    return pc 

def ingest(text: str, ns: str):
    pdf_splitter = get_splitter().create_documents([text])
    vectorstore = PineconeVectorStore.from_documents(
        documents=pdf_splitter,
        embedding=embeddings,
        # Make sure its index_name= not just index=
        index_name=settings.PINECONE_INDEX,
        # Namespace to label our files based on different companies
        namespace=ns)
    return vectorstore

def question(q: str, ns: list, top_k: int = 3, temp: int = 0):
    # Local import for lazy init 
    from openai import OpenAI

    # We only need the Client in this function so let's avoid building this object when its unnecessary
    ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Embed  our qestion and build context for our LLM
    # 
    # This is exactly the same as using your: client.embeddings.create(model='model', input="Question here") 
    question_embedded = embeddings.embed_query(q)

    # Using our index to query taking top K results.
    #
    # We've included metadata to grab the messages
    # 
    # We're using namespace to query the specific company's information ONLY 
    mass_results = []
    for namespace in ns:
        res = get_index().query(
            vector=question_embedded,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace
        )
        # res is an object with matches array so we extend this into our current mass_results array
        mass_results.extend(res['matches'])

    # Because we concat all of our matches we need to sort by score 
    mass_results.sort(key= lambda m : m['score'], reverse=True)
    # Based off of our k value we take the best 3 results 
    top_mass_results = mass_results[:top_k]

    # Building the context for our LLM 
    context = "\n\n".join(m['metadata']['text'] for m in top_mass_results)

    prompt = f"""
    You are an assistant with access to the following context from a document:

    {context}

    Answer the question based only on the above context.
    Question: {q}
    """

    ai_response = ai_client.chat.completions.create(
        model='gpt-4o',
        messages=[{'role':'user', 'content': prompt}],
        # We want 0 because its more direct and a 1-to-1 answer no fluff
        temperature=temp
    )

    return ai_response.choices[0].message.content

# Update & Delete: Helper Functions 
def delete_vector(namespace: str):
    # In order to Update we'll need to remove the original 
    #
    # Instead of using pinecone.delete_index(name=) --> Actually deleted the entire index
    # We use index.delete(namespace=)
    get_index().delete(delete_all=True, namespace=namespace)


def update_vector(text: str, ns: str, new_ns: str = None):
    # For us to "Update", we actually have to Delete the old vectors and reingest 
    #
    # We could loop through all vectors and replace them but the question is "What if our users upload a whole different file...?"
    delete_vector(ns)

    # # Reingest new content depending on the namespace 
    targeted_namespace = new_ns if new_ns else ns 
    ingest(text, targeted_namespace)

def update_namespace(old_ns: str, new_ns: str):
    # Copies the vectors into new namespace 
    #
    # Fetch Current Vector --> Upsert into new namespace 
    current_vectors = get_index().query(
        # Placeholder but 1536 is our dimension
        vector=[0.0] * 1536,
        # Fetching All Values 
        top_k=10000,    # Enough to grab all values in our Vectors 
        include_values=True,
        include_metadata=True,
        namespace=old_ns
    )

    # Copy over the ID, values and metadata (where the texts are )
    # 
    # Be sure you're iterating over the matches NOT the query object itself
    transformed_vectors = [
        {"id": v["id"], "values": v["values"], "metadata": v['metadata']}
        for v in current_vectors['matches']
    ]

    # Removing the old namespace vector 
    delete_vector(namespace=old_ns)
    # Update Insert (Creates one if not exists) --> It's going to 
    get_index().upsert(vectors=transformed_vectors, namespace=new_ns)
