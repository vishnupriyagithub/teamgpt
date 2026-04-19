from dotenv import load_dotenv
load_dotenv(override=True)
from llm.gemini import GeminiLLM
from llm.groq import GroqLLM
from cache.redis_cache import redis_client
from fastapi import FastAPI, UploadFile, File, Body, HTTPException, Depends
from dependencies.auth_dep import get_current_user
from auth.google_auth import verify_google_token
from auth.jwt_auth import create_jwt
# from models.user_store import get_or_create_user
from cache.redis_cache import get_cached_answer, set_cached_answer
from embedding import embed_texts, embed_query
import logging
from search.hybrid import keyword_search
from db import SessionLocal
from models.db_models import ChatMessage, Project
from db import SessionLocal
from models.db_models import User
from models.db_models import Document
logger = logging.getLogger(__name__)
from vector_store import get_project_collection
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
from utils.projects import save_project
from utils.text import split_text
# from llm.gemini import GeminiLLM
from llm.local import LocalLLM
# from vector_store import persist_chroma
from llm import get_llm
from db import engine
from models.db_models import Base
from models.db_models import Project


# Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/debug-auth")
def debug_auth():
  
    from auth.jwt_auth import create_jwt
    return {
        "google_client_id": bool(os.getenv("GOOGLE_CLIENT_ID")),
        "jwt_secret": bool(os.getenv("JWT_SECRET")),
        "load_dotenv_test": bool(os.getenv("GROQ_API_KEY"))
    }
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173", "https://teamgpt-frontend-sxpm.onrender.com"], 
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ANSWER_CACHE = {}
##########
# llm = LocalLLM()
llm = get_llm()
####
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "AI Project Assistant running"}

@app.get("/health")
def health():
    return Response(status_code=200)

# -----------------------------
# Upload Document
# -----------------------------
@app.post("/upload")
async def upload_document(
    project_id: str = Body(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    user_id = user["user_id"]
    from models.db_models import Project

    db = SessionLocal()

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

    # Allow creation if project doesn't exist yet (first upload)
    if not project:
        print("New project will be created")
    else:
        print("Existing project verified")

    db.close()
    print("UPLOAD STARTED")
    if not project_id.strip():
        raise HTTPException(status_code=400, detail="project_id is required")
    
    contents = await file.read()
    print("FILE READ DONE")
    if len(contents) > 2_000_000:  # ~2MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 2MB allowed.")
    
    
    text = contents.decode("utf-8", errors="ignore")
    chunks = split_text(text)
    print(f"TEXT SPLIT INTO {len(chunks)} CHUNKS")
    if not chunks:
        raise HTTPException(status_code=400, detail="No valid text found in the document.")
    print("STARTING EMBEDDINGS")
    vectors = embed_texts(chunks)
    print("EMBEDDINGS DONE")
    collection = get_project_collection(project_id)
    print("COLLECTION READY")
    doc_id = uuid.uuid4().hex

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[vectors[i]],
            ids=[f"{doc_id}_{i}"],
            metadatas=[{
                "project_id": project_id,
                "filename": file.filename,
                "chunk_index": i
            }]
        )
    print("CHROMA INSERT DONE")
    file_path = os.path.join(UPLOAD_DIR, f"{project_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)
                             
    # with open(os.path.join(UPLOAD_DIR, file.filename), "wb") as f:
        # f.write(contents)
        
    save_project(user_id, project_id)
    print("PROJECT SAVED")
    doc= Document(
        project_id=project_id,
        user_id=user_id,
        filename=file.filename,
        file_path=file_path
    )
    db = SessionLocal()
    db.add(doc) 
    db.commit()
    db.close()

    
    
    return {
        "message": "Uploaded & processed",
        "chunks": len(chunks)
    }


@app.get("/documents/{project_id}")
def get_documents(project_id: str, user=Depends(get_current_user)):
    db = SessionLocal()
    user_id = user["user_id"]
    
    doc =   db.query(Document).filter(
        Document.project_id == project_id,
        Document.user_id == user_id
        
    ).all()
    result = [
        {
            "filename": d.filename,
            "uploaded_at": d.created_at
        }
        for d in doc
    ]
    db.close()
    return {"documents": result}
# -----------------------------
# Ask Question (RAG)
# -----------------------------

def save_chat(project_id, user_id,role, content):
    
    db = SessionLocal()
    msg = ChatMessage(
        
        project_id=project_id,
        user_id=user_id,
        role=role,
        content=content
    )
    
    db.add(msg)
    db.commit()
    db.close()
    
@app.post("/ask")
def ask_question(
    project_id: str = Body(...),
    question: str = Body(...),
    user=Depends(get_current_user)
):
    print("🔥🔥🔥 ASK API HIT 🔥🔥🔥")
    print("QUESTION RECEIVED:", question)
    user_id = user["user_id"]
    db = SessionLocal()

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

    if not project:
        db.close()
        raise HTTPException(status_code=403, detail="Unauthorized project access")

    db.close()
    normalized_question = question.strip().lower()
    cache_key = f"{project_id}:{normalized_question}"
    print("QUESTION:", question)

    
    # collection = get_project_collection(project_id)
    # if cache_key in ANSWER_CACHE:
    #     print("ANSWER FROM CACHE")
    #     return{
    #         "answer": ANSWER_CACHE[cache_key],
    #         "cached": True,
    #         "used_context": "(from cache)"
    #     }
    cached = get_cached_answer(cache_key)
    if cached:
        print("ANSWER FROM REDIS CACHE")
        return{
            "answer": cached,
            "cached": True,
            "used_context": "(from cache)"
        }
    collection = get_project_collection(project_id)
    
    

    # 1. Embed the question
    query_vector = embed_query(question)
    print("QUERY VECTOR:", query_vector[:5])  # sample

    

    # 2. Retrieve relevant chunks
    
    vector_results = collection.query(
        query_embeddings=[query_vector],
        n_results=5
    )
    

    print("VECTOR RESULTS:", vector_results)

    
    
    vector_docs = vector_results.get("documents", [[]])[0] 
    print("VECTOR DOCS:", vector_docs)
    if not vector_docs:
        return {
            "answer": "I don't know. Not in scope of my knowledge.",
            "used_context": "",
            "cached": False
        }
    
    keyword_docs = keyword_search(
        question,
        vector_docs,
        top_k=2
    )

# 3. Merge + deduplicate
    final_docs = list(dict.fromkeys(vector_docs + keyword_docs))
    
    if not final_docs:
        return {
            "answer": "I don't know. Not in scope of my knowledge.",
            "used_context": "",
            "cached": False
        }
        

# 4. Build context
    context = " ".join(final_docs[:10])
    
    
    

    # 4. Build prompt
    prompt = f"""
You are a helpful assistant.

Use the context below to answer the question.
If the answer is partially available, try to answer as much as possible.

Context (retrieved using semantic + keyword search):
{context}

Question:
{question}
"""
    try:
        
        
    # 5. Generate answer using Gemini
        # answer = generate_answer(prompt)
        save_chat(project_id, user_id, "user", question)
        answer = llm.generate(prompt)
        save_chat(project_id, user_id, "assistant", answer)
        # if (not answer or len(answer.strip()) < 10 or "i don't know" in answer.lower()):
            
        #     return {
                
        #         "answer": "I don't know.",
        #         "used_context": context,
        #         "cached": False
        #     }
        # ANSWER_CACHE[cache_key] = answer
        set_cached_answer(cache_key, answer)
        print("FINAL CONTEXT:", context)
        print("RAW LLM ANSWER:", answer)
        return {
            
            "answer": answer,
            "used_context": context,
            "cached": False
        }
    except Exception as e:
        logger.error(f"LLM generation error: {str(e)}")
        print("LLM ERROR:", str(e))
        
        return {
            "answer": "I don't know.",
            "cached": False
        }
        
from utils.projects import get_projects
@app.get("/projects")
def list_projects(user=Depends(get_current_user)):
    # from utils.projects import load_projects
    user_id = user["user_id"]
    projects = get_projects(user_id)
    return {"projects": projects}

@app.get("/redis-test")
def redis_test():
    redis_client.set("hello", "world",ex=10)
    return {"value": redis_client.get("hello")}

@app.post("/auth/google")
def google_login(token: str = Body(..., embed=True)):
    user_info = verify_google_token(token)
    print("USER INFO FROM GOOGLE:", user_info)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    name= user_info.get("name") or "User"
    user_id = user_info.get("user_id") or user_info.get("sub")
    email = user_info.get("email")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Google token missing user ID")
    db = SessionLocal()
    
    existing_user = db.query(User).filter(User.id == user_id).first()

    if not existing_user:
        
        new_user = User(
            
            id=user_id,   # Google unique ID
            email=user_info.get("email"),
            name=user_info.get("name")
        )
        db.add(new_user)
        db.commit()

    db.close()
    user = {
    "user_id": user_id,
    "email": email,
    "name": name,
    "picture": user_info.get("picture")
    }

    jwt_token = create_jwt({
        "user_id": user_id,
        "email": user["email"],
        "name": user["name"]
    })

    return {
        "access_token": jwt_token,
        "user": user
    }

@app.get("/chat/{project_id}")
def get_chat(project_id: str, user=Depends(get_current_user)):
    db = SessionLocal()
    user_id = user["user_id"]
    from models.db_models import Project

    

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

    if not project:
        db.close()
        raise HTTPException(status_code=403, detail="Unauthorized project access")

    
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.project_id == project_id, ChatMessage.user_id == user_id)\
        .order_by(ChatMessage.created_at)\
        .all()

    result = [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

    db.close()
    return {"messages": result}