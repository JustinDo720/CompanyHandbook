# Company Handbook - AI-Powered Q&A

A modern **AI-powered company handbook** designed to streamline onboarding and internal Q&A. This project leverages a **RAG (Retrieval-Augmented Generation) pipeline** to process company PDFs and provide a chat-like interface for employees to query company policies, procedures, and guidelines efficiently.

---

## Features

- **RAG Pipeline**: Converts company PDFs into embeddings using OpenAI LLM and stores them in Pinecone for fast retrieval.
- **Chat Interface**: React frontend providing a seamless Q&A experience for employees.
- **Automated PDF Management**: Django CRON tasks clean old PDF vectors from Pinecone to maintain storage efficiency.
- **Background Tasks**: Celery + Beat for periodic tasks, including PDF processing and embedding updates.
- **Secure API**: Django REST Framework handles all backend operations securely.

---

## Tech Stack

- **Backend**: Django REST Framework  
- **Frontend**: React.js  
- **Vector Database**: Pinecone  
- **LLM**: OpenAI GPT (via embeddings & response generation)  
- **Task Queue**: Django Celery + Beat  
- **PDF Processing**: PyMuPDF (fitz) reading PDFs 

---

## Architecture Overview

1. **PDF Upload**  
   - Admin uploads new company PDFs via Django REST endpoints.  
2. **Embedding Generation**  
   - Celery tasks extract text from PDFs and generate embeddings using OpenAI.  
3. **Vector Storage**  
   - Embeddings stored in Pinecone under a **namespace per PDF**.  
4. **CRON Cleanup Task**  
   - A periodic task filters the `Namespace` model to identify old PDFs and removes outdated embeddings from Pinecone.  
5. **Q&A Chat**  
   - Users interact with the React frontend, which queries Pinecone for relevant embeddings and generates answers using GPT.  

---

## Development Phase 

Keeping Track of Development Progress

### 09/04

- [x] Building out Django Application Template 
- [x] Custom User + Handbook Model 
  - Set up Media Files in settings
  - Foreign key One-Many 
  - Create seperate app **(Remember to migrate Custom user first)**
  - File Uploads support PDF ONLY
- [x] CRUD Handbook --> Using Restframework 
  - Parital Updates 
  - Serializer Mixin + Url Hyperlink 
  - Multipart Form Parsers
- [ ] ~~Register Users~~ Tomorrow 

### 09/05

- [x] Set Up homepage for Django Restframework 
  - Make APiView with reverse links  
- [x] Work on User Auth + JWT 
  - SJWT + Djoser
  - Djoser requires custom `UserCreateSerializer` since we changed to a **Custom User Auth Model**
  - [Endpoints](https://djoser.readthedocs.io/en/latest/jwt_endpoints.html):
    - `company/users/` (Create User)
    - `/company/jwt/create/` (Login + JWT)
    - `/company/jwt/verify/` (Verify Access Token)
    - `/company/jwt/refresh/` (Refreshing Access Token)
- [x] List All Users
  - Comapnies Url now has an `app_name` so we updated all the url references to: `comapnies:<company_view_name>`
  - Hyperlinked Handbook to Companies and vice versa 
    - `serialiers.HyperlinkedRelatedField` 
- [ ] ~~Work on Pinecone + LLM~~ (Tomorrow) 
- [x] Guard our Handbook API (Auth ONLY)
  - Custom Permission?? --> IsOwnerOrAdmin --> `return obj.company == request.user`
  - `IsOwnerOrAdminHandbook` only applies to **Retrieve Update or Destroy** but cannot be applied on **List**

We also created two seperate Serializer for List vs Get Handbook API 
- Since we've updated the permissions for Owner or Admin we want to only allow the owners | admins to retrieve, update, destroy their own record 
- Listing Handbook
  - We've removed some important details like pdf link and the time it was created 
  - This allows **EVERYONE** to see that the record exists without seeing all the details 
- Retrieve Update Destroy Handbook 
  - Protected via `IsOwnerOrAdminHandbook` permission 
  - Other unauthorized users CANNOT see the important details...
