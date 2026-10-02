# Campus Knowledge Assistant

An AI-powered university knowledge assistant built using **Retrieval-Augmented Generation (RAG)**. The system answers questions from authorized university documents and provides source citations with role-based access control.

> **Status:** Project completed locally. Deployment is planned for a later stage.

## Features

- JWT authentication with bcrypt password hashing
- Role-Based Access Control (Student, Faculty, HOD, Admin)
- Admin-only PDF upload and document management
- PDF text extraction and automatic chunking
- PostgreSQL + pgvector semantic search
- Permission-aware document retrieval
- Sentence Transformer embeddings
- Cross-Encoder reranking
- Gemini-powered RAG answers
- Clickable `[Source N]` citations
- Chat history
- Admin user and permission management

## Architecture

```text
                    +----------------------+
                    |     React Frontend   |
                    |      Vite + React    |
                    +----------+-----------+
                               |
                               | HTTP / JSON
                               v
                    +----------------------+
                    |    FastAPI Backend   |
                    | Authentication + RBAC|
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
       +-------------+  +-------------+  +-------------+
       | PostgreSQL  |  | Embeddings  |  |   Gemini    |
       | + pgvector |  | + Reranker  |  |    LLM      |
       +-------------+  +-------------+  +-------------+
```

## RAG Pipeline

### Document ingestion

```text
PDF -> Text Extraction -> Chunking -> Embeddings -> PostgreSQL + pgvector
```

### Question answering

```text
User Question
    -> JWT Authentication
    -> Permission Check
    -> Embedding
    -> Vector Similarity Search
    -> Reranking
    -> Relevant Context
    -> Gemini
    -> Answer + Sources
```

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- python-jose
- Passlib
- bcrypt

### AI / NLP

- Sentence Transformers
- `all-MiniLM-L6-v2` for embeddings
- `cross-encoder/ms-marco-MiniLM-L-6-v2` for reranking
- Google Gemini API

### Database

- PostgreSQL
- pgvector

### Document Processing

- PyMuPDF

### Development

- VS Code
- Git
- GitHub

## Project Structure

```text
campus-knowledge-assistant/
|
+-- backend/
|   +-- admin_users.py
|   +-- auth.py
|   +-- chat.py
|   +-- chunking.py
|   +-- database.py
|   +-- documents.py
|   +-- embed_existing_chunks.py
|   +-- embeddings.py
|   +-- llm.py
|   +-- main.py
|   +-- models.py
|   +-- permissions.py
|   +-- rag_answer.py
|   +-- reranker.py
|   +-- retrieval.py
|   +-- schemas.py
|   +-- secure_search.py
|   +-- seed.py
|   +-- seed_admin.py
|   +-- semantic_search.py
|   +-- test_auth.py
|   +-- test_chunking.py
|   +-- requirements.txt
|   +-- .env.example
|   +-- uploads/
|
+-- frontend/
|   +-- public/
|   +-- src/
|   |   +-- AdminPanel.jsx
|   |   +-- App.jsx
|   |   +-- App.css
|   |   +-- index.css
|   |   +-- main.jsx
|   +-- package.json
|   +-- package-lock.json
|   +-- vite.config.js
|   +-- .env.example
|
+-- .gitignore
+-- README.md
```

## Local Setup

### Prerequisites

- Python 3.11
- Node.js and npm
- PostgreSQL
- PostgreSQL pgvector extension
- Git

### 1. Clone the repository

```bash
git clone https://github.com/preethika03/campus-knowledge-assistant.git
cd campus-knowledge-assistant
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
```

On Windows:

```cmd
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Backend environment variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/campus_assistant
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:5173
```

Never commit the real `.env` file or API keys to GitHub.

### 4. PostgreSQL setup

Create the database:

```sql
CREATE DATABASE campus_assistant;
```

Enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Start the backend

From `backend/`:

```bash
python -m uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 6. Frontend setup

In a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Roles and Access

| Role | Main access |
|---|---|
| Student | Authorized campus information |
| Faculty | Faculty-authorized information |
| HOD | HOD-authorized information |
| Admin | User, document, and permission management |

Public registration creates **Student** accounts. Admin users can create Faculty and HOD accounts from the Admin Panel.

## Document Permissions

Documents can be granted to individual users. Permission filtering happens before retrieved chunks are passed to the AI model.

```text
Document
  |
  +-- Student A -> Can View
  +-- Student B -> Cannot View
  +-- Faculty A -> Can View
```

## Example Questions

```text
What are the attendance requirements?
What is the prerequisite for AI301?
How many books can an undergraduate borrow?
What happens if a student cheats in an examination?
What is the penalty for plagiarism?
How many credits can a student register for?
```

The application should return an answer with citations such as:

```text
[Source 1]
[Source 2]
```

## API Endpoints

### Authentication

```text
POST /register
POST /login
GET  /users/me
```

### Documents

```text
POST  /documents/
GET   /documents/
POST  /documents/upload
POST  /documents/{document_id}/permissions
PATCH /documents/{document_id}/status
```

### Chat

```text
POST /chat/
GET  /chat/history
```

### Admin Users

```text
GET   /admin/users
POST  /admin/users
PATCH /admin/users/{user_id}/status
```

### Health

```text
GET /health
```

## Security

- JWT bearer authentication
- bcrypt password hashing
- Role-based authorization
- Document-level permissions
- Active/inactive account checks
- Admin-only document upload
- Admin-only user management
- Public registration restricted to Student role
- Secrets stored in environment variables
- `.gitignore` protection for secret files

## Testing

The backend includes tests for authentication and chunking. RAG behavior can also be tested by uploading different university policy PDFs and asking document-specific questions.

Example synthetic test topics:

- Course prerequisites and registration
- Disciplinary rules and punishments
- Examination rules and malpractice
- Attendance and leave
- Library rules and fines
- Academic integrity and plagiarism

These are useful for checking semantic retrieval, permission filtering, reranking, and citations.

## Deployment

Deployment is planned for a later stage.

The repository is prepared with:

- GitHub version control
- `requirements.txt`
- `.env.example`
- Configurable backend/frontend URLs
- PostgreSQL + pgvector architecture

Possible deployment architecture:

```text
React Frontend
     |
Frontend Hosting
     |
FastAPI API
     |
Managed PostgreSQL + pgvector
     |
Gemini API
```

## Future Improvements

- Page-level PDF citations
- Document preview
- Better document metadata
- More advanced permission management
- Automated RAG evaluation
- Response quality metrics
- Rate limiting
- Production monitoring
- Docker support
- Automated deployment
- Admin analytics dashboard

## Author

**Preethika**

Campus Knowledge Assistant - AI-powered university knowledge system.

GitHub: https://github.com/preethika03/campus-knowledge-assistant
