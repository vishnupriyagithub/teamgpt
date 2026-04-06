# llm/__init__.py
from config import LLM_PROVIDER, LM_STUDIO_BASE_URL, LM_STUDIO_MODEL, GEMINI_MODEL , GROQ_MODEL
from llm.local import LocalLLM
from llm.gemini import GeminiLLM
from llm.groq import GroqLLM

def get_llm():
    if LLM_PROVIDER == "local":
        return LocalLLM(LM_STUDIO_BASE_URL, LM_STUDIO_MODEL)
    elif LLM_PROVIDER == "gemini":
        return GeminiLLM(GEMINI_MODEL)
    elif LLM_PROVIDER == "groq":
        return GroqLLM(GROQ_MODEL)

    else:
        raise ValueError("Invalid LLM_PROVIDER")
