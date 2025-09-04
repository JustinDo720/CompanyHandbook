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