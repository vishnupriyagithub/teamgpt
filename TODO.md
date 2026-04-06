
✅ groq package available (user install)

## Remaining Steps
- [ ] Create backend/llm/groq.py (GroqLLM class)
- [ ] Install groq in backend/venv (`cd backend; .\\venv\\Scripts\\Activate.ps1; pip install groq`)
- [ ] Update backend/requirements.txt (+groq)
- [ ] Update backend/config.py (GROQ_MODEL, LLM_PROVIDER="groq")
- [ ] Update backend/llm/__init__.py (import/support groq)
- [ ] Update backend/main.py (use get_llm())
- [ ] User adds GROQ_API_KEY to backend/.env
- [ ] Test: uvicorn backend.main:app --reload + /ask

