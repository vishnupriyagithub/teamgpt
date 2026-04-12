# TeamGPT - Project Knowledge Assistant

[![Backend](https://img.shields.io/badge/FastAPI-Modern%20API-blue)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/React-19-brightgreen)](https://react.dev/)
[![LLM](https://img.shields.io/badge/Groq-Llama%203.3-orange)](https://groq.com/)

TeamGPT is a **full-stack RAG (Retrieval-Augmented Generation) application** for team project documentation. Upload documents to project-specific knowledge bases, chat with AI to query content using semantic + keyword search.

## 🚀 Features
- **Per-Project Knowledge Bases**: Upload docs → auto-chunk/embed → ChromaDB.
- **Hybrid RAG**: Vector (sentence-transformers) + BM25 keyword search → LLM answer.
- **LLM Support**: Groq (default), Gemini, Local (LM Studio).
- **Auth**: Google OAuth + JWT.
- **Persistence**: PostgreSQL (users/projects/chats/docs), Redis cache.
- **React UI**: Sidebar projects, real-time chat, file upload.
- **Limits**: 2MB/file, cached answers.

## 🛠 Tech Stack
### Backend
```
FastAPI | Uvicorn | SQLAlchemy (PostgreSQL) | ChromaDB | sentence-transformers | Groq | Redis
```
### Frontend
```
React 19 | Vite | Lucide Icons | Google OAuth
```

## 📦 Quick Start
1. **Clone & Install**
   ```
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

2. **Environment** (.env in root)
   ```
   DATABASE_URL=postgresql://user:pass@localhost/teamgpt
   GROQ_API_KEY=your_groq_key
   JWT_SECRET=supersecretkey
   GOOGLE_CLIENT_ID=your_google_client_id
   REDIS_URL=redis://localhost:6379
   ```

3. **Database**
   ```
   # Create DB/tables (run once)
   cd backend
   python -c "from db import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

4. **Run**
   **Terminal 1 (Backend):**
   ```
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   **Terminal 2 (Frontend):**
   ```
   cd frontend
   npm run dev
   ```
   Open http://localhost:5173

## 📱 Usage
1. **Login** with Google.
2. **New Project** (+ button).
3. **Upload** docs (⊕).
4. **Chat** - Ask questions about uploads.

## 🏗 Architecture
```
Frontend (React) ── JWT ──> Backend (FastAPI)
                          │
                 PostgreSQL  ChromaDB  Redis
                          │
                       Groq/ Gemini LLM
```

**RAG Flow**:
Query → Embed → Chroma (top5) + BM25 (top2) → Context → LLM → Cache → Response

## 🌐 API Endpoints
| Method | Endpoint | Auth | Desc |
|--------|----------|------|------|
| POST | `/auth/google` | No | Google login |
| GET | `/projects` | JWT | List projects |
| POST | `/upload` | JWT | Upload doc |
| POST | `/ask` | JWT | RAG query |
| GET | `/chat/{project_id}` | JWT | Chat history |
| GET | `/documents/{project_id}` | JWT | Docs list |

Docs: http://localhost:8000/docs

## 🔧 Customization
- **LLM**: Edit `config.py` → `LLM_PROVIDER="gemini"`
- **Embeddings**: Change model in `embedding.py`.
- **Redis**: Optional; falls back to in-mem.

## 🐛 Troubleshooting
- **CORS**: Check `allow_origins` in main.py.
- **Chroma**: `data/chroma/` perms.
- **DB**: Verify `DATABASE_URL`, run `create_all`.
- **Groq**: Check API key/limits.

## 📈 Future
- WebSockets for real-time chat.
- Multi-user roles.
- PDF/Office parsing.
- Admin dashboards.

**Built with ❤️ for team productivity.**

